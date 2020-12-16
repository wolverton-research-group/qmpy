from rest_framework import generics
from rest_framework.exceptions import ValidationError, ParseError
import django_filters.rest_framework
from qmpy.web.serializers.optimade import OptimadeStructureSerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.materials.entry import Composition
from qmpy.utils import query_to_Q, parse_formula_regex

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from qmpy.rester import qmpy_rester
from django.shortcuts import render_to_response

from collections import OrderedDict
from qmpy.utils import oqmd_optimade as oqop
import time
import datetime

BASE_URL = qmpy_rester.REST_OPTIMADE


class OptimadeStructureDetail(generics.RetrieveAPIView):
    queryset = FormationEnergy.objects.filter(fit="standard")
    serializer_class = OptimadeStructureSerializer


class OptimadePagination(LimitOffsetPagination):
    default_limit = 50
    offset_query_param = 'page_offset'
    limit_query_param = 'page_limit'
    def get_paginated_response(self, page_data):
        data = page_data["data"]
        request = page_data["request"]

        full_url = request.build_absolute_uri()
        representation = full_url.replace(BASE_URL, "")

        time_now = time.time()
        time_stamp = datetime.datetime.fromtimestamp(time_now).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        _oqmd_final_query = page_data['meta']['django_query'] if 'django_query' in page_data['meta'] else None
        _warnings         = page_data['meta']['warnings']     if 'warnings'     in page_data['meta'] else []
        if (not _warnings) and (not _oqmd_final_query):
            _warnings = ["_oqmd_NoFilterWarning: No filters were provided in the query"]
        meta_list = [
                        ("query", {
                                      "representation"   : representation,
                                      "_oqmd_final_query": _oqmd_final_query
                                  }
                        ),
                        ("api_version", "1.0.0"),
                        ("time_stamp", time_stamp),
                        (
                            "data_returned",
                            min(
                                self.get_limit(request),
                                self.count - self.get_offset(request),
                               ),
                        ),
                        ("data_available", self.count),
                        (
                            "more_data_available",
                            (self.get_next_link() != None)
                            or (self.get_previous_link() != None),
                        ),
                        (
                            "provider", 
                            OrderedDict(
                                [
                                    ("name","OQMD"),
                                    ("description","The Open Quantum Materials Database"),
                                    ("prefix", "oqmd"),
                                    ("homepage", "http://oqmd.org"),
                                ])
                        ),
                        ("warnings", _warnings),
                        ("response_message", "OK")
                    ]
                        

        return Response(
            OrderedDict(
                [
                    (
                        "links",
                        OrderedDict(
                            [
                                ("next", self.get_next_link()),
                                ("previous", self.get_previous_link()),
                                (
                                    "base_url",
                                    {
                                        "href": BASE_URL,
                                        "meta": {"_oqmd_version": "1.0"},
                                    },
                                ),
                            ]
                        ),
                    ),
                    ("resource", {}),
                    ("data", data),
                    ("meta", OrderedDict(meta_list)),
                ]
            )
        )


class OptimadeStructureList(generics.ListAPIView):
    serializer_class = OptimadeStructureSerializer
    pagination_class = OptimadePagination
    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
        fes, meta_info = self.filter(fes)
        return (fes, meta_info)

    def list(self, request, *args, **kwargs):
        query_set, meta_info = self.get_queryset()
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        page_data = {"data"    : serializer.data, 
                     "request" : self.request,
                     "meta"    : meta_info }
        return self.get_paginated_response(page_data)

    def filter(self, fes):
        request = self.request

        filters = request.GET.get("filter", False)

        if not filters:
            meta_data = {"warnings": ["_oqmd_NoFilterWarning: No filters were provided in the query. Returning all structures"],}
            return fes, meta_data

        # shortcut to get all stable phases
        filters = filters.replace("stability=0", "stability<=0")

        filters = filters.replace("&", " AND ")
        filters = filters.replace("|", " OR ")
        filters = filters.replace("~", " NOT ")
        try:
            q, meta_info = query_to_Q(filters)
        except:
            raise ParseError
        if not q:
            return ([],meta_info)
        fes = fes.filter(q)

        return (fes,meta_info)

def OptimadeInfoData(request):
    data = oqop.get_optimade_data("info")
    return render_to_response("api/plain_text.html", {"data":data})

def OptimadeVersionsData(request):
    data = oqop.get_optimade_data("versions")
    return render_to_response("api/plain_text.html", {"data":data})

def OptimadeLinksData(request):
    data = oqop.get_optimade_data("links")
    return render_to_response("api/plain_text.html", {"data":data})

def OptimadeStructuresInfoData(request):
    data = oqop.get_optimade_data("info.structures")
    return render_to_response("api/plain_text.html", {"data":data})


