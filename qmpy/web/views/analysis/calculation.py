from django.shortcuts import render_to_response
from django.template import RequestContext
import os

from qmpy.models import Calculation
from qmpy.analysis.vasp.calculation import VaspError
from ..tools import get_globals

from bokeh.embed import components

def calculation_view(request, calculation_id):
    calculation = Calculation.objects.get(pk=calculation_id)
    data = get_globals()
    data['calculation'] = calculation
    data['stdout'] = ''
    data['stderr'] = ''

    if os.path.exists(os.path.join(calculation.path, 'stdout.txt')):
        with open(os.path.join(calculation.path, 'stdout.txt')) as fr:
            data['stdout'] = fr.read()
    if os.path.exists(os.path.join(calculation.path, 'stderr.txt')):
        with open(os.path.join(calculation.path, 'stderr.txt')) as fr:
            data['stderr'] = fr.read()
    try:
        data['incar'] = ''.join(calculation.read_incar())
    except VaspError:
        data['incar'] = 'Could not read INCAR'

    if not calculation.dos is None:
        script, div = components(calculation.dos.bokeh_plot)
        data['dos'] = script
        data['dosdiv'] = div

    return render_to_response('analysis/calculation.html',
            data, RequestContext(request))
