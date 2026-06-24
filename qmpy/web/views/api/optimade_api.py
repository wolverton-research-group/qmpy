from rest_framework import generics, status
from rest_framework.exceptions import APIException
from qmpy.web.serializers.optimade import OptimadeStructureSerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.utils import query_to_Q

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes
from django.http import HttpResponse

from collections import OrderedDict
from qmpy.utils import oqmd_optimade as oqop
from qmpy.utils.oqmd_optimade.config import (
    error_document,
    response_meta,
)


class OptimadeAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail, status_code=None, code=None, source=None):
        super().__init__(detail, code=code)
        if status_code is not None:
            self.status_code = status_code
        self.optimade_code = code
        self.optimade_source = source


class OptimadeRequestMixin(object):
    renderer_classes = [JSONRenderer]
    allowed_query_parameters = {
        "api_hint",
        "dimension_slices",
        "email_address",
        "filter",
        "page_limit",
        "page_offset",
        "response_fields",
        "response_format",
        "sort",
    }

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        for parameter in request.query_params:
            if parameter in self.allowed_query_parameters or parameter.startswith(
                "_oqmd_"
            ):
                continue
            raise OptimadeAPIException(
                "Unrecognized query parameter: {}".format(parameter),
                source={"parameter": parameter},
            )

        response_format = request.query_params.get("response_format", "json")
        if response_format != "json":
            raise OptimadeAPIException(
                "Unsupported response format: {}".format(response_format),
                source={"parameter": "response_format"},
            )

        api_hint = request.query_params.get("api_hint")
        is_versioned = "/optimade/v1" in request.path
        if api_hint and not is_versioned and api_hint not in {"v1", "v1.3"}:
            raise OptimadeAPIException(
                "The requested API version is not supported: {}".format(api_hint),
                status_code=553,
                code="VersionNotSupported",
                source={"parameter": "api_hint"},
            )
        if "dimension_slices" in request.query_params:
            raise OptimadeAPIException(
                "The dimension_slices query parameter is not implemented.",
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                source={"parameter": "dimension_slices"},
            )

    def handle_exception(self, exc):
        if isinstance(exc, OptimadeAPIException):
            return Response(
                error_document(
                    self.request,
                    str(exc.detail),
                    exc.status_code,
                    code=exc.optimade_code,
                    source=exc.optimade_source,
                ),
                status=exc.status_code,
            )
        response = super().handle_exception(exc)
        if response is not None and response.status_code >= 400:
            if isinstance(response.data, dict):
                detail = response.data.get("detail", "Request failed")
            else:
                detail = str(response.data)
            response.data = error_document(
                self.request, str(detail), response.status_code
            )
        return response


def _static_request_error(request):
    """Validate query parameters for info and links endpoints."""
    allowed = {"api_hint", "response_format"}
    for parameter in request.query_params:
        if parameter not in allowed and not parameter.startswith("_oqmd_"):
            detail = "Unrecognized query parameter: {}".format(parameter)
            return Response(
                error_document(
                    request,
                    detail,
                    400,
                    source={"parameter": parameter},
                ),
                status=400,
            )
    response_format = request.query_params.get("response_format", "json")
    if response_format != "json":
        detail = "Unsupported response format: {}".format(response_format)
        return Response(
            error_document(
                request,
                detail,
                400,
                source={"parameter": "response_format"},
            ),
            status=400,
        )
    api_hint = request.query_params.get("api_hint")
    if api_hint and "/optimade/v1" not in request.path and api_hint not in {
        "v1",
        "v1.3",
    }:
        detail = "The requested API version is not supported: {}".format(api_hint)
        return Response(
            error_document(request, detail, 553, code="VersionNotSupported"),
            status=553,
        )
    return None


class OptimadeStructureDetail(OptimadeRequestMixin, generics.RetrieveAPIView):
    queryset = FormationEnergy.objects.filter(fit="standard")
    serializer_class = OptimadeStructureSerializer

    def retrieve(self, request, *args, **kwargs):
        structure_id = request.path.strip("/").split("/")[-1]
        self.queryset = self.queryset.filter(id=structure_id)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        _data = OrderedDict(serializer.data)
        data = OrderedDict([("id", _data["id"]), ("type", _data["type"])])
        del _data["id"]
        del _data["type"]
        data["attributes"] = _data
        return Response(
            OrderedDict(
                [
                    ("links", {"self": request.build_absolute_uri()}),
                    ("data", data),
                    (
                        "meta",
                        response_meta(
                            request,
                            data_returned=1,
                            data_available=FormationEnergy.objects.filter(
                                fit="standard"
                            ).count(),
                        ),
                    ),
                ]
            )
        )


class OptimadePagination(LimitOffsetPagination):
    default_limit = 50
    offset_query_param = "page_offset"
    limit_query_param = "page_limit"

    def get_paginated_response(self, page_data):
        _data = page_data["data"]
        data = []
        for _item in _data:
            item = OrderedDict([("id", _item["id"]), ("type", _item["type"])])
            del _item["id"]
            del _item["type"]
            item["attributes"] = _item
            data.append(item)
        request = page_data["request"]

        _oqmd_final_query = (
            page_data["meta"]["django_query"]
            if "django_query" in page_data["meta"]
            else None
        )
        _warnings = (
            page_data["meta"]["warnings"] if "warnings" in page_data["meta"] else []
        )
        if (not _warnings) and (not _oqmd_final_query):
            _warnings = [
                {
                    "type": "warning",
                    "detail": "_oqmd_NoFilterWarning: No filters were provided in the query",
                }
            ]
        meta = response_meta(
            request,
            more_data_available=self.get_next_link() is not None,
            data_returned=self.count,
            data_available=FormationEnergy.objects.filter(fit="standard").count(),
            warnings=_warnings,
            _oqmd_data_in_response=len(data),
            _oqmd_final_query=_oqmd_final_query,
        )

        return Response(
            OrderedDict(
                [
                    (
                        "links",
                        OrderedDict(
                            [
                                ("next", self.get_next_link()),
                                ("previous", self.get_previous_link()),
                                ("self", request.build_absolute_uri()),
                            ]
                        ),
                    ),
                    ("data", data),
                    ("meta", meta),
                ]
            )
        )


class OptimadeStructureList(OptimadeRequestMixin, generics.ListAPIView):
    serializer_class = OptimadeStructureSerializer
    pagination_class = OptimadePagination

    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
        fes, meta_info = self.filter(fes)
        return (fes, meta_info)

    def list(self, request, *args, **kwargs):
        requested_fields = request.query_params.get("response_fields")
        if requested_fields:
            available_fields = set(self.serializer_class.Meta.fields)
            unknown_fields = set(requested_fields.split(",")) - available_fields
            if unknown_fields:
                field = sorted(unknown_fields)[0]
                raise OptimadeAPIException(
                    "Unknown response field: {}".format(field),
                    source={"parameter": "response_fields"},
                )
        query_set, meta_info = self.get_queryset()
        sort = request.query_params.get("sort")
        if sort:
            sort_fields = {
                "id": "id",
                "_oqmd_delta_e": "delta_e",
                "_oqmd_stability": "stability",
            }
            django_sort = []
            for field in sort.split(","):
                descending = field.startswith("-")
                name = field[1:] if descending else field
                if name not in sort_fields:
                    raise OptimadeAPIException(
                        "Property is not sortable: {}".format(name),
                        source={"parameter": "sort"},
                    )
                django_sort.append(
                    ("-" if descending else "") + sort_fields[name]
                )
            query_set = query_set.order_by(*django_sort)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        page_data = {
            "data": serializer.data,
            "request": self.request,
            "meta": meta_info,
        }
        return self.get_paginated_response(page_data)

    def filter(self, fes):
        request = self.request

        filters = request.GET.get("filter", False)

        if not filters:
            meta_data = {
                "warnings": [
                    {
                        "type": "warning",
                        "detail": "_oqmd_NoFilterWarning: No filters were provided in the query. Returning all structures",
                    }
                ],
            }
            return fes, meta_data

        q, meta_info = query_to_Q(filters)
        if not q:
            return ([], meta_info)
        fes = fes.filter(q)

        return (fes, meta_info)


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def OptimadeInfoData(request):
    error = _static_request_error(request)
    if error is not None:
        return error
    return Response(oqop.get_optimade_data("info", request))


@api_view(["GET"])
def OptimadeVersionsData(request):
    data = oqop.get_optimade_data("versions", request)
    return HttpResponse(data, content_type="text/csv; header=present")


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def OptimadeVersionPage(request, version=None):
    if version in {"1", "1.3", "1.3.0"}:
        detail = "The requested OPTIMADE endpoint does not exist."
        return Response(error_document(request, detail, 404), status=404)
    detail = "OPTIMADE API version v{} is not supported; use v1.".format(version)
    return Response(
        error_document(request, detail, 553, code="VersionNotSupported"), status=553
    )


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def OptimadeLinksData(request):
    error = _static_request_error(request)
    if error is not None:
        return error
    return Response(oqop.get_optimade_data("links", request))


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def OptimadeStructuresInfoData(request):
    error = _static_request_error(request)
    if error is not None:
        return error
    return Response(oqop.get_optimade_data("info.structures", request))
