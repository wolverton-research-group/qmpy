import json


def write_info():
    data = {
        "data": {
            "type": "info",
            "id": "/",
            "attributes": {
                "api_version": "1.0",
                "available_api_versions": [
                    {"url": "http://oqmd.org/optimade/", "version": "1.0"},
                    {"url": "http://oqmd.org/optimade/v1/", "version": "1.0"},
                ],
                "formats": ["json", "xml", "yaml"],
                "entry_types_by_format": {
                    "json": ["structures"],
                    "xml": ["structures"],
                    "yaml": ["structures"],
                },
                "available_endpoints": ["structures", "info", "links", "versions"],
                "is_index": "false",
            },
        }
    }

    json.dump(data, open("optimade_info.json", "w"))


def write_info_structures():
    formats = ["json", "xml", "yaml"]
    properties = json.load(open("optimade_info_properties.json","r"))
    output_fields_by_format = {item:[jtem for jtem in properties] for item in formats}
    data = {
        "data": {
            "description": "a structures entry",
            "properties": properties,
            "formats": formats,
            "output_fields_by_format": output_fields_by_format,
        }
    }
    json.dump(data, open("optimade_info_structures.json", "w"))


def write_links_info():
    data = {
        "data": [
            {
                "type": "links",
                "id": "oqmd",
                "attributes": {
                    "name": "OQMD.org",
                    "description": "Open Quantum Materials Database",
                    "base_url": "http://oqmd.org/optimade/",
                    "homepage": "http://oqmd.org",
                    "link_type": "root",
                },
            },
            {
                "type": "links",
                "id": "optimade",
                "attributes": {
                    "name": "Materials Consortia",
                    "description": "List of OPTIMADE providers maintained by the Materials Consortia organisation",
                    "base_url": "https://providers.optimade.org",
                    "homepage": "https://optimade.org",
                    "link_type": "providers",
                },
            },
        ]
    }
    json.dump(data, open("optimade_links.json", "w"))


write_info()
write_info_structures()
write_links_info()
