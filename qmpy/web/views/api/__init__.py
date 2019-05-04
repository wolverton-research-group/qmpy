from django.shortcuts import render_to_response
from django.template import RequestContext

from entry_list_view import *
from calculation_list_view import *
from formationenergy_list_view import *
from api_gen import *
from search_data import *
from optimade_api import *

def api_view(request):
    return render_to_response('api/index.html', {})
