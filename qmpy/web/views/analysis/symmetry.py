from django.shortcuts import render_to_response
from django.template import RequestContext

from qmpy.models import Spacegroup, Operation
import StringIO
from ..tools import get_globals

def sg_view(request, spacegroup):
    spacegroup = Spacegroup.objects.get(pk=spacegroup)
    structures = spacegroup.structure_set.filter(label='input')[:10]
    data = get_globals()
    data['spacegroup'] = spacegroup
    data['structures'] = structures
    data['request'] = request
    return render_to_response('analysis/symmetry/spacegroup.html',
            data,
            RequestContext(request))

def op_view(request, operation):
    operation = Spacegroup.objects.get(id=operation)
    data = get_globals()
    data['operation'] = operation
    data['request'] = request
    return render_to_response('analysis/symmetry/operation.html',
            data,
            RequestContext(request))

