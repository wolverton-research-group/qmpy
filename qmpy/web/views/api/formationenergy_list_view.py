from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.formationenergy import FormationEnergySerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.materials.composition import Composition
from qmpy.materials.element import Element
from qmpy.utils import query_to_Q, parse_formula_regex
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.db.models import F, Q
import operator

from qmpy.rester import qmpy_rester
from collections import OrderedDict

import time
import datetime

DEFAULT_LIMIT = 50
BASE_URL = qmpy_rester.REST_OQMDAPI

class QmpyPagination(LimitOffsetPagination):
    default_limit = 50
    def get_paginated_response(self, page_data):
        data = page_data["data"]
        request = page_data["request"]
        full_url = request.build_absolute_uri()
        representation = full_url.replace(BASE_URL, '')

        time_now = time.time()
        time_stamp = datetime.datetime.fromtimestamp(time_now).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        return Response(OrderedDict([
            ('links', 
             OrderedDict([('next', self.get_next_link()),
                          ('previous', self.get_previous_link()),
              ('base_url', {
                  "href": BASE_URL,
                  "meta":{'_oqmd_version': "1.0"}
              })
             ])
            ),
            ('resource', {}),
            ('data', data),
            ('meta', 
             OrderedDict([
                 ("query", {"representation": representation}),
                 ("api_version", "1.0"),
                 ("time_stamp", time_stamp), 
                 ("data_returned", min(self.get_limit(request), 
                                       self.count-self.get_offset(request))),
                 ("data_available", self.count),
                 ('comments',page_data["comments"]),
                 ('query_tree',page_data["query_tree"]),
                 ("more_data_available", (self.get_next_link() != None) or \
                                         (self.get_previous_link() != None))
             ])
            ),
            ("response_message", "OK")
        ]))
        


class FormationEnergyDetail(generics.RetrieveAPIView):
    queryset = FormationEnergy.objects.all()
    serializer_class = FormationEnergySerializer

class FormationEnergyList(generics.ListAPIView):
    serializer_class = FormationEnergySerializer
    pagination_class = QmpyPagination #LimitOffsetPagination
    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
        fes = self.icsd_filter(fes)
        fes = self.composition_filter(fes)
        fes = self.duplicate_filter(fes)
        fes = self.filter(fes)

        sort_fes = self.request.GET.get('sort_by', False)
        if not sort_fes:
            return fes
        else:
            limit = self.request.GET.get('limit')
            sort_offset = self.request.GET.get('sort_offset')
            try:
                limit = int(limit)
            except:
                limit = DEFAULT_LIMIT
            try:
                sort_offset = int(sort_offset)
            except:
                sort_offset = 0
            desc = self.request.GET.get('desc', False)

        if sort_fes == 'stability':
            fes = self.sort_by_stability(fes, limit, sort_offset, desc)
        elif sort_fes == 'delta_e':
            fes = self.sort_by_delta_e(fes, limit, sort_offset, desc)

        return fes

    
    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        page = self.paginate_queryset(query_set)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            page_data = {"data": serializer.data, 
                         "request": self.request,
                         "comments": '', #self.query_comments,
                         "query_tree": '',
                        }
            return self.get_paginated_response(page_data)

        serializer = self.get_serializer(query_set, many=True)
        return Response(serializer.data)
    

    def icsd_filter(self, fes):
        request = self.request
        ificsd = request.GET.get('icsd', None)
        
        if ificsd == None:
            return fes
        elif ificsd in ['False', 'false', 'F', 'f']:
            return fes.exclude(entry__path__contains='/icsd/')
        elif ificsd in ['True', 'true', 'T', 't']:
            return fes.filter(entry__path__contains='/icsd/')

        return fes

    def composition_filter(self, fes):
        """
        Valid url parameter inputs:
           # 1. ?composition=Fe2O3
            2. ?composition=Fe-O
            3. ?composition={Fe,Ni}O
            4. ?composition={3d}2O3
        """
        request = self.request

        comp = request.GET.get('composition', False)
        if not comp:
            return fes

        if '{' and '}' in comp:
            c_dict_lst = parse_formula_regex(comp)
            f_lst = []
            for cd in c_dict_lst:
                f = ' '.join(['%s%g' % (k, cd[k]) for k in sorted(cd.keys())])
                f_lst.append(f)
            fes = fes.filter(composition__formula__in=f_lst)
        elif '-' in comp:
            c_lst = comp.strip().split('-')
            dim = len(c_lst)
            q_lst = [Q(composition__element_list__contains=s+'_') 
                     for s in c_lst]
            combined_q = reduce(operator.or_, q_lst)
            combined_q = reduce(operator.and_, 
                                [
                                    combined_q, 
                                    Q(composition__ntypes__lte=dim)
                                ]
                                )

            ex_q_lst = [Q(composition__element_list__contains=e.symbol+'_')
                        for e in Element.objects.exclude(symbol__in=c_lst)]
            combined_q_not = reduce(operator.or_, ex_q_lst)

            fes = fes.filter(combined_q).exclude(combined_q_not)
        else:
            c = Composition.get(comp)
            fes = fes.filter(composition=c)

        return fes

    def duplicate_filter(self, fes):
        """
        Valid url parameter inputs:
            ?noduplicate=True
        """
        request = self.request

        dup = request.GET.get('noduplicate', False)

        if dup in ['T', 'True', 'true', 'TRUE', 't']:
            fes = fes.filter(entry__id=F("entry__duplicate_of__id"))

        return fes

    def filter(self, fes):
        """
        Valid attributes:
            element, generic, prototype, spacegroup,
            volume, natoms, ntypes, stability,
            delta_e, band_gap

        Requirments:
            1. Space padding is required between expression. 
            2. For each epression, space is not allowed.
            3. Operators include: 'AND', 'OR'
            4. '(' and ')' can be used to change precedence
            5. For numerical attributes, we can have '>' or '<' conditions.
            Valid examples:
                'element=Mn AND band_gap>1'
                '( element=O OR element=S ) AND natoms<3'
            Invalid examples:
                'element = Fe'
                '( element=Fe And element=O)'

        Additionally, instead of multiple 'element' expressions, we can use
        'element_set' expression to combine elements in the filter.

        Format of element_set expression:
            ',': AND operator
            '-': OR operator
            '(', ')': to change precedence
            Examples:
                element_set=Al;O,H
                element_set=(Mn;Fe),O
        """
        request = self.request

        filters = request.GET.get('filter', False)

        if not filters:
            return fes

        # shortcut to get all stable phases
        filters = filters.replace('stability=0', 'stability<=0')

        # replace'&' ,'|' and '~'  to 'AND', 'OR' and 'NOT', respectively
        filters = filters.replace('&', ' AND ')
        filters = filters.replace('|', ' OR ')
        filters = filters.replace('~', ' NOT ')
        q = query_to_Q(filters)
        if not q:
            return []
        fes = fes.filter(q)
        return fes

    def sort_by_stability(self, fes, limit=DEFAULT_LIMIT, sort_offset=0, desc=False):
        if desc in ['T', 't', 'True', 'true']:
            ordered_fes = fes.order_by('-stability')
        else:
            ordered_fes = fes.order_by('stability')
        return ordered_fes[sort_offset:sort_offset+limit]

    def sort_by_delta_e(self, fes, limit=DEFAULT_LIMIT, sort_offset=0, desc=False):
        if desc in ['T', 't', 'True', 'true']:
            ordered_fes = fes.order_by('-delta_e')
        else:
            ordered_fes = fes.order_by('delta_e')
        return ordered_fes[sort_offset:sort_offset+limit]
