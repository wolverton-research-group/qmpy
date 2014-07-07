from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf

from qmpy.models import Formation, MetaData
from qmpy.utils import *

def disco_view(request):
    search = None
    data = {}

    if request.method == 'POST':
        p = request.POST
        search = p.get('search', '')
        data.update(p)
    if search is None:
        return render_to_response('analysis/discovery.html',
                data,
                RequestContext(request))

    # stable prototypes
    form = Formation.objects.filter(fit='standard', 
            stability__lt=0.0,
            entry__meta_data__value='prototype')
    form = form.exclude(stability=None)
    if search:
        form = form.filter(composition__element_set=search)

    # get rid of those with ICSD entries at the same composition
    form1 = form.exclude(composition__entry__meta_data__value='icsd')
    result1 = form.values_list('composition', 'entry__prototype__name', 'delta_e')
    result1 = [[ format_comp(parse_comp(c)), proto, de ] for c, proto, de in result1 ]

    # find cases where there _is_ an ICSD entry at the same composition
    form2 = form.filter(composition__entry__meta_data__value='icsd')
    result2 = form2.values_list('composition', flat=True)

#    result3 = []
#    for c in form.values_list('composition', flat=True):
#        cdict = parse_comp(c).keys()
#        sname = '-'.join(sorted(cdict))
#
#        md = MetaData.get('space', sname)
#        icsd = md.entry_set.filter(path__contains='icsd')
#        if not icsd.exists():
#            result3.append(c)

    data = {'type1': result1,
            'type2': result2}
#            'type3': result3}
    data.update(csrf(request))

    return render_to_response('analysis/discovery.html', data)

