"""Documents served by the OPTIMADE introspection endpoints."""

import json
import os
from collections import OrderedDict

from .config import API_VERSION, base_url, response_meta


PROPERTY_DEFINITION_SCHEMA = (
    "https://schemas.optimade.org/meta/v1.2/optimade/property_definition.json"
)
STANDARD_STRUCTURE_PROPERTIES = {
    "elements",
    "nelements",
    "elements_ratios",
    "chemical_formula_descriptive",
    "chemical_formula_reduced",
    "chemical_formula_anonymous",
    "dimension_types",
    "nperiodic_dimensions",
    "lattice_vectors",
    "cartesian_site_positions",
    "nsites",
    "species_at_sites",
    "species",
    "structure_features",
    "space_group_it_number",
    "space_group_symbol_hall",
    "space_group_symbol_hermann_mauguin",
}
CORE_PROPERTIES = {"id", "type", "last_modified"}


def _legacy_properties():
    filename = os.path.join(
        os.path.dirname(__file__), "grammar", "optimade_info_structures.json"
    )
    with open(filename, "r") as handle:
        return json.load(handle)["data"]["properties"]


def _property_reference(name, legacy):
    """Reference the canonical definition and add OQMD support metadata."""
    if name in CORE_PROPERTIES:
        property_id = "https://schemas.optimade.org/defs/v1.2/properties/core/{}".format(
            name
        )
    else:
        property_id = (
            "https://schemas.optimade.org/defs/v1.2/properties/optimade/structures/{}"
        ).format(name)
    return OrderedDict(
        [
            ("$ref", property_id),
            ("description", legacy["description"]),
            (
                "x-optimade-implementation",
                {
                    "sortable": bool(legacy.get("sortable")),
                    "query-support": (
                        "all mandatory" if legacy.get("_oqmd_queryable") else "none"
                    ),
                },
            ),
        ]
    )


def _custom_property_definition(name, legacy):
    type_map = {
        "float": "number",
        "integer": "integer",
        "list": "array",
        "string": "string",
        "timestamp": "string",
    }
    optimade_type = legacy["type"]
    json_type = type_map[optimade_type]
    definition = OrderedDict(
        [
            (
                "$id",
                "urn:oqmd:optimade:property:{}".format(name),
            ),
            ("$schema", PROPERTY_DEFINITION_SCHEMA),
            ("title", name.replace("_", " ").strip()),
            (
                "x-optimade-definition",
                {
                    "label": "{}_oqmd".format(name.strip("_")),
                    "kind": "property",
                    "format": "1.2",
                    "version": "1.0.0",
                    "name": name,
                },
            ),
            ("x-optimade-type", optimade_type),
            ("type", [json_type, "null"]),
            ("description", legacy["description"]),
            ("x-optimade-unit", legacy.get("unit") or "inapplicable"),
            (
                "x-optimade-implementation",
                {
                    "sortable": bool(legacy.get("sortable")),
                    "query-support": (
                        "all mandatory" if legacy.get("_oqmd_queryable") else "none"
                    ),
                },
            ),
        ]
    )
    if json_type == "array":
        definition["items"] = {}
    if optimade_type == "timestamp":
        definition["format"] = "date-time"
    return definition


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
    }
    legacy_properties.update(serializer_additions)
    for name, legacy in legacy_properties.items():
        if name in CORE_PROPERTIES or name in STANDARD_STRUCTURE_PROPERTIES:
            properties[name] = _property_reference(name, legacy)
        else:
            properties[name] = _custom_property_definition(name, legacy)
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
