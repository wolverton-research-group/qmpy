import json
import os


def get_optimade_data(label):
    """
    Function providing data for all optimade endpoints, except the data-endpoint

    Currently served end-points are:
        1. Info endpoint : Provides general information about the API implementation
        2. Info/Structures endpoint : Provides information specific to the structures-data
                                      that OQMD currently supports in RESTful queries
        3. Versions endpoint : Lists the versions of optimade grammar that OQMD supports
        4. Links endpoint : Links to all the relevent DBs that OQMD provides/associates.

    """
    if label == "info":
        filename = os.path.join(
            os.path.dirname(__file__), "grammar", "optimade_info.json"
        )
        data = json.load(open(filename, "r"))
        return json.dumps(data, indent=2)
    elif label == "versions":
        return "version\n1"
    elif label == "info.structures":
        filename = os.path.join(
            os.path.dirname(__file__), "grammar", "optimade_info_structures.json"
        )
        data = json.load(open(filename, "r"))
        return json.dumps(data, indent=2)
    elif label == "links":
        filename = os.path.join(
            os.path.dirname(__file__), "grammar", "optimade_links.json"
        )
        data = json.load(open(filename, "r"))
        return json.dumps(data, indent=2)

    else:
        return "{}"
