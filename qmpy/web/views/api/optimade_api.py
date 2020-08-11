from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.optimade import OptimadeStructureSerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.materials.entry import Composition
from qmpy.utils import query_to_Q, parse_formula_regex

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from qmpy.rester import qmpy_rester

from collections import OrderedDict

import time
import datetime

BASE_URL = qmpy_rester.REST_OPTIMADE

class OptimadeStructureDetail(generics.RetrieveAPIView):
    queryset = FormationEnergy.objects.filter(fit='standard')
    serializer_class = OptimadeStructureSerializer

class OptimadePagination(LimitOffsetPagination):
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
                 ("more_data_available", (self.get_next_link() != None) or \
                                         (self.get_previous_link() != None))
             ])
            ),
            ("response_message", "OK")
        ]))

class OptimadeStructureList(generics.ListAPIView):
    serializer_class = OptimadeStructureSerializer
    pagination_class = OptimadePagination

    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
        fes = self.filter(fes)
        return fes

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        page = self.paginate_queryset(query_set)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            page_data = {"data": serializer.data, "request": self.request}
            return self.get_paginated_response(page_data)

        serializer = self.get_serializer(query_set, many=True)
        return Response(serializer.data)

    def filter(self, fes):
        request = self.request

        filters = request.GET.get('filter', False)

        if not filters:
            return fes

        # shortcut to get all stable phases
        filters = filters.replace('stability=0', 'stability<=0')

        filters = filters.replace('&', ' AND ')
        filters = filters.replace('|', ' OR ')
        filters = filters.replace('~', ' NOT ')
        q = query_to_Q(filters)
        if not q:
            return [] 
        fes = fes.filter(q)

        return fes
