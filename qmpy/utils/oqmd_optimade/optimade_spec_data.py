"""Documents served by the OPTIMADE introspection endpoints."""

import json
import os
from collections import OrderedDict

from .config import API_VERSION, base_url, response_meta


def _legacy_properties():
    filename = os.path.join(
        os.path.dirname(__file__), "grammar", "optimade_info_structures.json"
    )
    with open(filename, "r") as handle:
        return json.load(handle)["data"]["properties"]


def _entry_info_property(legacy):
    """Return the property metadata shape required by OPTIMADE 1.2."""
    return OrderedDict(
        [
            ("description", legacy["description"]),
            ("unit", legacy.get("unit")),
            ("sortable", bool(legacy.get("sortable"))),
            ("type", legacy["type"]),
        ]
    )


def _structures_properties():
    legacy_properties = _legacy_properties()
    legacy_properties.pop("_oqmd_direct_site_positions", None)
    legacy_properties["id"].update(
        {
            "description": "String identifier of the OQMD formation-energy record.",
            "type": "string",
            "_oqmd_queryable": True,
        }
    )
    legacy_properties["type"].update(
        {
            "description": "The OPTIMADE entry type; always structures.",
            "type": "string",
            "_oqmd_queryable": True,
        }
    )
    legacy_properties["last_modified"].update(
        {
            "description": "Last modification timestamp, currently unknown in OQMD.",
            "type": "timestamp",
        }
    )
    properties = OrderedDict()
    serializer_additions = {
        "immutable_id": {
            "description": "Optional immutable identifier; unavailable in OQMD.",
            "type": "string",
            "sortable": False,
        },
        "chemical_formula_hill": {
            "description": "Chemical formula in Hill notation; unavailable in OQMD.",
            "type": "string",
            "sortable": False,
        },
        "space_group_symmetry_operations_xyz": {
            "description": "Crystallographic symmetry operations; unavailable in OQMD.",
            "type": "list",
            "sortable": False,
        },
        "space_group_it_number": {
            "description": "International Tables for Crystallography space-group number.",
            "type": "integer",
            "sortable": False,
            "_oqmd_queryable": False,
        },
        "space_group_symbol_hall": {
            "description": "Hall space-group symbol.",
            "type": "string",
            "sortable": False,
            "_oqmd_queryable": False,
        },
        "space_group_symbol_hermann_mauguin": {
            "description": "Hermann-Mauguin space-group symbol.",
            "type": "string",
            "sortable": False,
            "_oqmd_queryable": False,
        },
        "space_group_symbol_hermann_mauguin_extended": {
            "description": "Extended Hermann-Mauguin space-group symbol; unavailable in OQMD.",
            "type": "string",
            "sortable": False,
        },
        "assemblies": {
            "description": "Correlated site assemblies; unavailable in OQMD.",
            "type": "list",
            "sortable": False,
        },
    }
    legacy_properties.update(serializer_additions)
    for name, legacy in legacy_properties.items():
        properties[name] = _entry_info_property(legacy)
    return properties


def get_optimade_data(label, request):
    """Return a Python response document for a non-entry endpoint."""
    if label == "versions":
        return "version\n1\n"

    meta = response_meta(request)
    if label == "info":
        data = {
            "type": "info",
            "id": "/",
            "attributes": {
                "api_version": API_VERSION,
                "available_api_versions": [
                    {"url": base_url(request, versioned=True), "version": API_VERSION}
                ],
                "formats": ["json"],
                "entry_types_by_format": {"json": ["structures"]},
                "available_endpoints": ["structures", "info", "links"],
                "is_index": False,
            },
        }
    elif label == "info.structures":
        properties = _structures_properties()
        data = {
            "type": "info",
            "id": "structures",
            "description": "OQMD crystal structures and their calculated properties.",
            "properties": properties,
            "formats": ["json"],
            "output_fields_by_format": {"json": list(properties)},
        }
    elif label == "links":
        data = [
            {
                "type": "links",
                "id": "oqmd",
                "attributes": {
                    "name": "OQMD",
                    "description": "The Open Quantum Materials Database",
                    "base_url": base_url(request),
                    "homepage": "https://oqmd.org",
                    "link_type": "root",
                },
            }
        ]
    else:
        data = None
    return OrderedDict([("meta", meta), ("data", data)])
