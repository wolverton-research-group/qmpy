from django.shortcuts import render_to_response
from django.template import RequestContext

from qmpy.models import Calculation

def download_home(request):
    return render_to_response('download.html', {})
