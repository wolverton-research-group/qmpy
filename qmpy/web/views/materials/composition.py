from tempfile import mkstemp
import os.path
from pprint import pprint

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from ..tools import get_globals
from qmpy import *

ndict = {1:'elements',
         2:'binary phases',
         3:'ternary phases',
         4:'quaternary phases',
         5:'pentenary phases',
         6:'hexanary phases'}

def construct_flot(phase_dict):
    data = []
    for p, v in phase_dict.items():
        series = {'label':p.name, 'data':v}
        data.append(series)
    return json.dumps(data)

def composition_view(request, search=None):
    data = get_globals()
    data['search'] = ''
    composition = ''
    space = []
    if request.method == 'POST':
        p = request.POST
        search = p.get('search', '')
        data.update(p)
    if not search:
        return render_to_response('materials/composition.html',
                data,
                RequestContext(request))

    if search.count('-') == 0:
        composition = search
    else:
        space = search

    if composition:
        comp = Composition.get(composition)
        ps = PhaseSpace('-'.join(comp.comp.keys()))
        ps.infer_formation_energies()
        data['pd'] = ps.phase_diagram.get_flot_script("phasediagram")
        data['search'] = composition
        data['composition'] = comp
        data['plot'] = comp.relative_stability_plot.get_flot_script()
        data['results'] = comp.entries
        energy, gs = ps.gclp(comp.name)
        data['gs'] = Phase.from_phases(gs)
        data['phases'] = gs
        data['compound'] = comp.ground_state
        if len(gs) == 1:
            data['singlephase'] = True 
        else:
            data['singlephase'] = False
        #data['singlephase'] = ( len(gs) == 1 )
        data['space'] = '-'.join(comp.comp.keys())
        return render_to_response('materials/composition.html', 
                data,
                RequestContext(request))
    elif space:
        ps = PhaseSpace(space)
        ps.infer_formation_energies()
        data['search'] = space
        data['pd'] = ps.phase_diagram.get_flot_script("phasediagram")
        ##data['stable'] = []
        ##for p in ps.stable:
        ##    if p.formation is None:
        ##        continue
        ##    data['stable'].append(p.formation.energy)
        ## Fe-Ti-Sb: what's the problem?
        data['stable'] = [ p.formation.entry for p in ps.stable ]
        comps = Composition.get_list(space)
        results = defaultdict(list)
        for c in comps:
            results['-'.join(sorted(c.space))] += c.entries
        for k,v in results.items():
            results[k] = sorted(v, key=lambda x:
                    1000 if x.energy is None else x.energy)
        results = sorted(results.items(), key=lambda x: -len(x[0].split('-')))
        data['results'] = results
        return render_to_response('materials/phasespace.html', 
                data,
                RequestContext(request))

def generic_composition_view(request, search=None):
    data = {'search':search}
    composition = ''
    space = []
    if request.method == 'POST':
        p = request.POST
        search = p.get('search', '')
        data.update(p)
    if not search:
        return render_to_response('materials/generic_composition.html',
                data,
                RequestContext(request))
        
    gc = GenericComposition(search)
    data['gc'] = gc
    return render_to_response('materials/generic_composition.html', 
            data,
            RequestContext(request))
