import json
import os

def get_optimade_data(label):
    if label=="info":
        filename = os.path.join(os.path.dirname(__file__), "./grammar", "optimade_info.json")
        data  =json.load(open(filename,"r"))
        return json.dumps(data,indent=4)
    elif label=="versions":
        return "version \n 1"
    elif label=="info.structures":
        filename = os.path.join(os.path.dirname(__file__), "./grammar", 
                                  "optimade_info_structures.json")
        data  =json.load(open(filename,"r"))
        return json.dumps(data,indent=4)
    elif label=="links":
        filename = os.path.join(os.path.dirname(__file__), "./grammar", "optimade_links.json")
        data  =json.load(open(filename,"r"))
        return json.dumps(data,indent=4)

    else:
        return "{}"
