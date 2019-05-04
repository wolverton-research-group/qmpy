from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.optimade import OptimadeStructureSerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.materials.entry import Composition
from qmpy.utils import Token, parse_formula_regex

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from collections import OrderedDict

import time
import datetime

BASE_URL = "http://larue.northwestern.edu:9000/optimade"

class OptimadePagination(LimitOffsetPagination):
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
                 ("data_returned", min(self.get_limit(request), self.count)),
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
        return Response(serialzer.data)

    def filter(self, fes):
        request = self.request

        filters = request.GET.get('filter', False)

        if not filters:
            return fes

        # replace 'AND' and 'OR' to '&' and '|', respectively
        filters = filters.replace('AND', '&')
        filters = filters.replace('OR', '|')

        t = Token(filters, optimade=True)
        q = t.evaluate_filter(origin='formationenergy')
        fes = fes.filter(q)

        return fes
