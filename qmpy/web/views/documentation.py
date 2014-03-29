from django.shortcuts import render_to_response
from django.template import RequestContext

from qmpy.models import Calculation

def docs_view(request):
    return render_to_response('documentation/index.html', {})

def structures_docs(request):
    return render_to_response('documentation/structures.html', {})

def vasp_docs(request):
    return render_to_response('documentation/vasp.html', {})

def pots_docs(request):
    return render_to_response('documentation/pots.html', {})

def overview_docs(request):
    return render_to_response('documentation/overview.html', {})

def pubs_docs(request):
    return render_to_response('documentation/pubs.html', {})
