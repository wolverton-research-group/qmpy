from django.template import RequestContext
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.forms.models import modelform_factory

from qmpy import *

qfile = open(INSTALL_PATH+'/configuration/qfiles/local.q').read()

def new_host_view(request):
    data = {'nodes':30,
            'ppn':8,
            'walltime':3600*24*7,
            'sub_script':'/usr/local/bin/qsub',
            'check_queue':'/usr/local/maui/bin/showq',
            'sub_text':qfile}
    if request.method == 'POST':
        data.update(request.POST)
        host = Host(**data)
        print host
        host.save()
    return render_to_response("computing/new_host.html", 
            data,
            RequestContext(request))

