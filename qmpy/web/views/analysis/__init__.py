from django.shortcuts import render_to_response
from django.template import RequestContext

from symmetry import *
from visualize import *
from thermodynamics import *
from calculation import *

def analysis_view(request):
    return render_to_response('analysis/index.html', {})
