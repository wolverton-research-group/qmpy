from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.context_processors import csrf

from qmpy.data import element_groups


def element_group_view(request):
    data = {}
    data['element_groups'] = dict([(k, ', '.join(v)) for k, v in list(element_groups.items())])
    data['groups'] = sorted(element_groups.keys())

    return render_to_response('materials/element_groups.html', 
            data,
            RequestContext(request))

