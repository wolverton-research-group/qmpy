from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.optimade import OptimadeStructureSerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.materials.entry import Composition
from qmpy.utils import Token, parse_formula_regex
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response

class OptimadePagination(PageNumberPagination):
#class OptimadePagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': self.get_next_link(),
            'count': self.page.paginator.count,
            'results': data,
        })

class OptimadeStructureList(generics.ListAPIView):
    serializer_class = OptimadeStructureSerializer
    pagination_class = OptimadePagination

    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
        fes = self.composition_filter(fes)
        fes = self.filter(fes)

        return fes

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        page = self.paginate_queryset(query_set)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(query_set, many=True)
        return Response(serialzer.data)

    def composition_filter(self, fes):
        """
        Valid url parameter inputs:
            1. ?composition=Fe2O3
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
        else:
            c_lst = comp.strip().split('-')
            cs = Composition.get_list(c_lst)
            if len(cs) == 1:
                c = cs[0]
            else:
                c = cs
            fes = fes.filter(composition=c)

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
            '-': AND operator
            ',': OR operator
            '(', ')': to change precedence
            Examples:
                element_set=Al,O-H
                element_set=(Mn,Fe)-O
        """
        request = self.request

        filters = request.GET.get('filters', False)

        if not filters:
            return fes

        # replace 'AND' and 'OR' to '&' and '|', respectively
        filters = filters.replace('AND', '&')
        filters = filters.replace('OR', '|')

        t = Token(filters, optimade=True)
        q = t.evaluate_filter(origin='formationenergy')
        fes = fes.filter(q)

        return fes
