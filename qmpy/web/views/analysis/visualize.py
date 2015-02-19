from tempfile import mkstemp
import os.path

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

import cStringIO
from qmpy import *
from ..tools import get_globals

global custom_data
custom_data = None

def vis_data(request):
    global custom_data
    data = {'crystal_data':"""Cr Te O
 1.0
7.016000 0.000000 0.000000
0.000000 7.545000 0.000000
-1.637391 0.000000 9.589209
Cr O Te
4 22 8
direct
 0.319200 0.501900 0.384200
 0.680800 0.001900 0.115800
 0.680800 0.498100 0.615800
 0.319200 0.998100 0.884200
 0.205000 0.644000 0.212100
 0.795000 0.144000 0.287900
 0.795000 0.356000 0.787900
 0.205000 0.856000 0.712100
 0.500000 0.000000 0.500000
 0.500000 0.500000 0.000000
 0.127000 0.314000 0.342900
 0.873000 0.814000 0.157100
 0.873000 0.686000 0.657100
 0.127000 0.186000 0.842900
 0.468000 0.375000 0.262300
 0.532000 0.875000 0.237700
 0.532000 0.625000 0.737700
 0.468000 0.125000 0.762300
 0.563000 0.641000 0.451700
 0.437000 0.141000 0.048300
 0.437000 0.359000 0.548300
 0.563000 0.859000 0.951700
 0.158000 0.649000 0.486600
 0.842000 0.149000 0.013400
 0.842000 0.351000 0.513400
 0.158000 0.851000 0.986600
 0.139700 0.859900 0.176200
 0.860300 0.359900 0.323800
 0.860300 0.140100 0.823800
 0.139700 0.640100 0.676200
 0.672300 0.861800 0.415800
 0.327700 0.361800 0.084200
 0.327700 0.138200 0.584200
 0.672300 0.638200 0.915800"""}
    p = request.POST
    if request.method == 'POST':
        custom_data = p.get('crystal_data', '')
        data['crystal_data'] = custom_data
        f = cStringIO.StringIO()
        f.write(custom_data)
        s = io.read(f)
        #s.symmetrize()
        data['structure'] = s
    data.update(csrf(request))
    custom_data = data['crystal_data']
    return render_to_response('analysis/view_data.html',
            get_globals(data),
            RequestContext(request))

def jsmol(request):
    global custom_data
    f = cStringIO.StringIO()
    f.write(custom_data)
    return HttpResponse(f.getvalue(), mimetype="plain/text")
