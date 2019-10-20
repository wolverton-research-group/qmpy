from django.shortcuts import render_to_response
from django.template import RequestContext

from qmpy.utils import *

def deposit_view(request):
    return render_to_response('materials/deposit.html', {})
