from django.shortcuts import render_to_response
from django.template import RequestContext

from qmpy.models import Spacegroup, Operation
import StringIO

def sg_view(request, spacegroup):
    spacegroup = Spacegroup.objects.get(pk=spacegroup)
    structures = spacegroup.structure_set.filter(label='input')[:10]
    return render_to_response('analysis/symmetry/spacegroup.html', 
            {'spacegroup':spacegroup,
                'structures':structures,
                'request':request})
            #RequestContext(request))

def op_view(request, operation):
    operation = Spacegroup.objects.get(id=operation)
    return render_to_response('analysis/symmetry/operation.html', 
            {'operation':operation,
                'request':request})
            #RequestContext(request))

