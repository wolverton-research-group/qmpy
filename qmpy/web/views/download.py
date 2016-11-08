from django.shortcuts import render_to_response
from django.template import RequestContext

from tools import get_globals
from qmpy.data.meta_data import DatabaseUpdate

def download_home(request):
    data = get_globals()
    data['updated_on'] = DatabaseUpdate.value()
    return render_to_response('download.html', data)
