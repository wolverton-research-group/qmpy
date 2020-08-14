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
        if None in  [p.formation.stability for p in ps.phases]:
            ps.compute_stabilities(save=True, reevaluate=True)
        ps.infer_formation_energies()
        if ps.shape == (3, 0):
            data['pd3d'] = ps.phase_diagram.get_plotly_script_3d("phasediagram")
        data['pd'] = ps.phase_diagram.get_flot_script("phasediagram")
        data['search'] = composition
        data['composition'] = comp
        data['plot'] = comp.relative_stability_plot(data=ps.data).get_flot_script()
        data['results'] = FormationEnergy.objects.filter(composition=comp,
                                                         fit='standard').order_by('delta_e')
        pro_name = [None if len(fe.entry.projects)==0 else fe.entry.projects[0].name for fe in data['results']]
        finish_time = [None if len(fe.entry.tasks)==0 else fe.entry.tasks[0].finished for fe in data['results']]
        data['results_project'] = zip(data['results'], pro_name, finish_time)
        
        run_entry = Entry.objects.filter(composition=comp,formationenergy=
                             None).filter(id=F("duplicate_of__id"))
        run_pro = [None if len(en.projects)==0 else en.projects[0].name for en in run_entry]
        create_time = [None if len(en.tasks)==0 else en.tasks[0].created for en in run_entry]
        data['running'] = zip(run_entry, run_pro, create_time)
        data['space'] = '-'.join(comp.comp.keys())

        if comp.ntypes == 1:
            energy, gs = ps.gclp(comp.name)
            data['gs'] = Phase.from_phases(gs)
            data['gclp_phases'] = gs.keys()
            data['phase_links'] = [p.link for p in data['gclp_phases']]
            data['current_phase'] = ps.phase_dict[comp.name]
            data['phase_type'] = 'stable'
            data['delta_h'] = data['gs'].energy 
            data['decomp_en'] = - data['current_phase'].stability
        elif comp.name in ps.phase_dict:
            energy, gclp_phases = ps.compute_stability(comp)

            data['gs'] = Phase.from_phases(gclp_phases)
            data['current_phase'] = ps.phase_dict[comp.name]
            data['gclp_phases'] = gclp_phases.keys()
            data['phase_links'] = [p.link for p in data['gclp_phases']]

            if ps.phase_dict[comp.name].stability <= 0:
                data['phase_type'] = 'stable'
                data['delta_h'] = data['gs'].energy + data['current_phase'].stability
                data['decomp_en'] = - data['current_phase'].stability
            else:
                data['phase_type'] = 'unstable'
                data['delta_h'] = data['gs'].energy 
                data['hull_dis'] = data['current_phase'].stability
        else:
            energy, gs = ps.gclp(comp.name)
            data['gs'] = Phase.from_phases(gs)
            data['gclp_phases'] = gs.keys()
            data['phase_links'] = [p.link for p in data['gclp_phases']]
            data['phase_type'] = 'nophase'
            data['delta_h'] = data['gs'].energy 
        return render_to_response('materials/composition.html', 
                data,
                RequestContext(request))
    elif space:
        ps = PhaseSpace(space)
        if None in [p.formation.stability for p in ps.phases]:
            ps.compute_stabilities(save=True, reevaluate=True)
            ps = PhaseSpace(space)
        ps.infer_formation_energies()
        data['search'] = space
        if ps.shape == (3, 0):
            data['pd3d'] = ps.phase_diagram.get_plotly_script_3d("phasediagram")
        data['pd'] = ps.phase_diagram.get_flot_script("phasediagram")
        ##data['stable'] = []
        ##for p in ps.stable:
        ##    if p.formation is None:
        ##        continue
        ##    data['stable'].append(p.formation.energy)
        ## Fe-Ti-Sb: what's the problem?
        data['stable'] = [ p.formation for p in ps.stable ]
        pro_name = [None if len(fe.entry.projects)==0 else fe.entry.projects[0].name for fe in data['stable']]
        finish_time = [None if len(fe.entry.tasks)==0 else fe.entry.tasks[0].finished for fe in
                       data['stable']]
        data['stable'] = zip(data['stable'], pro_name, finish_time)

        
        ## The following step is really slow. Will be removed in future! 
        ## < Mohan
        # results = defaultdict(list)
        # comps = Composition.get_list(space) 
        # for c in comps:
        #     results['-'.join(sorted(c.space))] += c.entries

        ## Updated code to get entries in a phase space
        results = defaultdict(list)
        for p in ps.phases:
            c = p.formation.composition
            results['-'.join(sorted(c.space))] += [p.formation]
        ## Mohan >

        for k,v in results.items():
            results[k] = sorted(v, key=lambda x:
                    1000 if x.stability is None else x.stability)
            pro_name = [None if len(fe.entry.projects)==0 else fe.entry.projects[0].name for fe in results[k]]
            finish_time = [None if len(fe.entry.tasks)==0 else fe.entry.tasks[0].finished for fe in
                          results[k]]
            results[k] = zip(results[k], pro_name, finish_time)
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
