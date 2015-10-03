from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf

from qmpy.models import Formation, MetaData
from qmpy.utils import *
from ..tools import get_globals

def disco_view(request):
    search = None
    data = get_globals()

    if request.method == 'POST':
        p = request.POST
        search = p.get('search', '')
        data.update(p)
    if search is None:
        return render_to_response('materials/discovery.html',
                data,
                RequestContext(request))

    # stable prototypes
    form_all = Formation.objects.filter(fit='standard', 
            stability__lt=0.0,
            entry__meta_data__value='prototype')
    form_all = form_all.exclude(stability=None)
    if search:
        form_all = form_all.filter(composition__element_set=search)

    # get rid of those with ICSD entries at the same composition
    form_not_icsd = form_all.exclude(composition__entry__meta_data__value='icsd').distinct()
    res_not_icsd = form_not_icsd.values_list('composition', 'entry__prototype__name', 'delta_e')
    res_not_icsd = [[ format_comp(parse_comp(c)), proto, de ] for c, proto, de
            in res_not_icsd ]

    # find cases where there _is_ an ICSD entry at the same composition
    res_icsd = []
    form_icsd = form_all.filter(composition__entry__meta_data__value='icsd').distinct()
    for fe in form_icsd:
        if fe.entry.id != fe.entry.duplicate_of.id:
            continue
        proto_name = fe.entry.prototype.name if fe.entry.prototype is not None else 'None'
        res_icsd.append([ format_comp(fe.composition.comp), proto_name, fe.delta_e ])
        

    ####res_icsd = form_icsd.values_list('composition', 'entry__prototype__name', 'delta_e')
    ####res_icsd = [[ format_comp(parse_comp(c)), proto, de ] for c, proto, de in
    ####        res_icsd ]

#    result3 = []
#    for c in form.values_list('composition', flat=True):
#        cdict = parse_comp(c).keys()
#        sname = '-'.join(sorted(cdict))
#
#        md = MetaData.get('space', sname)
#        icsd = md.entry_set.filter(path__contains='icsd')
#        if not icsd.exists():
#            result3.append(c)

    data = {'not_icsd': res_not_icsd,
            'icsd': res_icsd}
#            'type3': result3}
    data.update(csrf(request))

    return render_to_response('materials/discovery.html', data)

