from tempfile import mkstemp
import os.path
import cStringIO
import pulp
import json

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from qmpy import *
from qmpy.analysis.thermodynamics import *
from ..tools import get_globals

def construct_flot(phase_dict):
    data = []
    for p, v in phase_dict.items():
        series = {'label':p.name, 'data':v}
        data.append(series)
    return json.dumps(data)

def gclp_view(request):
    data = {'composition':'',
            'phase_data':'',
            'per_atom':True,
            'energy':None,
            'phase_comp':{}}
    data = get_globals(data)

    if request.method == 'POST':
        p = request.POST
        if p.get('search'):
            comp = parse_comp(p['search'])
            bounds = '-'.join(comp.keys())
            data['search'] = p['search']

        if p['action'] == 'submit':
            ps = PhaseSpace(bounds)
            data['phase_data'] = ps.phase_dict.values()

        elif p['action'] == 're-evaluate':
            indices = p.getlist('indices')
            pdata = PhaseData()
            for i in indices:
                c = p['composition_%s' % i]
                t = p['formationenergy_%s' % i]
                phase = Phase(composition=c, energy=float(t))
                phase.id = p['id_%s' % i]
                phase.use = ( p['use_%s' % i] == 'on' )
                pdata.add_phase(phase)
            data['phase_data'] = pdata.phases
            ps = PhaseSpace(bounds, data=pdata)

        data['energy'], phases = ps.gclp(comp)
        data['plot'] = construct_flot(phases)
        data['energy'] /= sum(comp.values())
        data['phase_comp'] = dict(phases)
        data['pstr'] = Phase.from_phases(phases).name
        for k, v in data['phase_comp'].items():
            data['phase_comp'][k] /= sum(k.nom_comp.values())
    data.update(csrf(request))
    return render_to_response('analysis/gclp.html',
            data,
            RequestContext(request))

def phase_diagram_view(request):
    data = {'search': '',
            'chem_pots': '',
            'stability':0.25}
    if request.method == 'POST':
        p = request.POST
        if p.get('search'):
            data['search'] = p['search']
        if p.get('chem_pots'):
            data['chem_pots'] = p['chem_pots']

        if p['action'] == 'submit':
            print data["chem_pots"]
            ps = PhaseSpace(data['search'], mus=data['chem_pots'])
            if ps.shape[0] > 0:
                data['phase_data'] = ps.phase_dict.values()
            else:
                data['phase_data'] = ps.phases

        elif p['action'] == 're-evaluate':
            indices = p.getlist('indices')
            pdata = PhaseData()
            for i in indices:
                c = p['composition_%s' % i]
                t = p['formationenergy_%s' % i]
                phase = Phase(composition=c, energy=float(t))
                phase.id = int(p['id_%s' % i])
                phase.use = ( p['use_%s' % i] == 'on' )
                phase.show_label = ( p['label_%s' % i] == 'on' )
                pdata.add_phase(phase)
            data['phase_data'] = pdata.phases
            ps = PhaseSpace(data['search'], mus=data['chem_pots'], data=pdata,
                    load=None)

            if p.get('stability') and not data["chem_pots"]:
                ps.compute_stabilities()
                data['stability'] = p.get('stability')
                for phase in ps._phases:
                    if phase.stability > float(p.get('stability', 0.25)):
                        phase.use = False
                        phase.show_label = False

        data['flotscript'] = ps.phase_diagram.get_flot_script()
        data['renderer'] = ps.renderer
    return render_to_response('analysis/phase_diagram.html',
            get_globals(data),
            RequestContext(request))
