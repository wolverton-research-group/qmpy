from django.shortcuts import render

from qmpy.models import Spacegroup, Operation
from ..tools import get_globals

def sg_view(request, spacegroup):
    spacegroup = Spacegroup.objects.get(pk=spacegroup)
    structures = spacegroup.structure_set.filter(label='input')[:10]
    data = get_globals()
    data['spacegroup'] = spacegroup
    data['structures'] = structures
    data['request'] = request
    return render(request,'analysis/symmetry/spacegroup.html',
                  context=data)

def op_view(request, operation):
    operation = Spacegroup.objects.get(id=operation)
    data = get_globals()
    data['operation'] = operation
    data['request'] = request
    return render(request,'analysis/symmetry/operation.html',
                  context=data)

