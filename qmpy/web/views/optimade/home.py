from django.template import RequestContext
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
import requests, json

from qmpy import *
from qmpy.rester import qmpy_rester as qr
import datetime

def optimade_home(request):
    with qr.QMPYRester() as q:
        kwargs = {'limit':1}
        data = q.get_entries(verbose=False, **kwargs)

    output = {}
    output["links"] = {}
    output["links"]["next"] = data["next"] # Place holder
    output["links"]["base_url"] = {"href": "larue.northwestern.edu:9000",
                                   "meta": {}}
    
    if data["next"]:
        next_flag = "True"
    else:
        next_flag = "False"

    output["resource"] = {}
    output["data"] = data["results"]
    output["meta"] = {"query": {"representation": request.get_full_path()},
                      "api_version": "v0.0",
                      "time_stamp": datetime.datetime.now().isoformat(),
                      "data_returned": len(data["results"]),
                      "data_available": data["count"],
                      "last_id": "id", # Place holder
                      "more_data_available": next_flag
                     }


    json_out = json.dumps(output, indent=4)

    context = {'json_out': json_out}

    return render_to_response("optimade/home.html", 
            context,
            RequestContext(request))
