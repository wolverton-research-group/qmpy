"""Shared configuration and response helpers for the OQMD OPTIMADE API."""

import datetime
from collections import OrderedDict


API_VERSION = "1.3.0"
API_MAJOR_VERSION = "1"
SCHEMA_URL = "https://schemas.optimade.org/json-schema/v1.3.0/optimade.json"
PROVIDER = OrderedDict(
    [
        ("name", "OQMD"),
        ("description", "The Open Quantum Materials Database"),
        ("prefix", "oqmd"),
        ("homepage", "https://oqmd.org"),
    ]
)


def timestamp_now():
    """Return an RFC 3339 UTC timestamp (supported on Python 3.9)."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def query_representation(request):
    """Return the URL portion following the active OPTIMADE base URL."""
    path = request.get_full_path()
    marker = "/optimade"
    remainder = path.split(marker, 1)[1] if marker in path else path
    if remainder.startswith("/v1.3.0"):
        remainder = remainder[len("/v1.3.0") :]
    elif remainder.startswith("/v1.3"):
        remainder = remainder[len("/v1.3") :]
    elif remainder.startswith("/v1"):
        remainder = remainder[len("/v1") :]
    return remainder or "/"


def base_url(request, versioned=False):
    """Build the deployment-aware OPTIMADE base URL from the request."""
    root = request.build_absolute_uri("/optimade/")
    if versioned:
        return "{}v{}/".format(root, API_MAJOR_VERSION)
    return root


def response_meta(request, more_data_available=False, **extra):
    """Construct metadata common to every JSON OPTIMADE response."""
    meta = OrderedDict(
        [
            ("api_version", API_VERSION),
            ("query", {"representation": query_representation(request)}),
            ("more_data_available", bool(more_data_available)),
            ("schema", SCHEMA_URL),
            ("time_stamp", timestamp_now()),
            ("provider", PROVIDER.copy()),
            (
                "implementation",
                {
                    "name": "qmpy",
                    "version": "1.6.0",
                    "source_url": "https://github.com/wolverton-research-group/qmpy",
                    "issue_tracker": "https://github.com/wolverton-research-group/qmpy/issues",
                },
            ),
        ]
    )
    meta.update(extra)
    return meta


def error_document(request, detail, status, code=None, source=None):
    """Build a JSON:API-compatible OPTIMADE error response document."""
    error = OrderedDict([("status", str(status)), ("title", detail), ("detail", detail)])
    if code is not None:
        error["code"] = code
    if source is not None:
        error["source"] = source
    return OrderedDict(
        [
            ("meta", response_meta(request)),
            ("errors", [error]),
        ]
    )
