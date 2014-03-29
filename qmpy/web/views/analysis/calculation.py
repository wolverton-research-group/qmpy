from django.shortcuts import render_to_response
from django.template import RequestContext
import os.path

from qmpy.models import Calculation

def calculation_view(request, calculation_id):
    calculation = Calculation.objects.get(pk=calculation_id)
    data = {
            'calculation':calculation,
            'stdout':'', 'stderr':''
            }
    if os.path.exists(calculation.path+'/stdout.txt'):
        data['stdout'] = open(calculation.path+'/stdout.txt').read()
    if os.path.exists(calculation.path+'/stderr.txt'):
        data['stderr'] = open(calculation.path+'/stderr.txt').read()
    if not calculation.dos is None:
        data['dos'] = calculation.dos.plot.get_flot_script()
    return render_to_response('analysis/calculation.html', 
            data, RequestContext(request))
