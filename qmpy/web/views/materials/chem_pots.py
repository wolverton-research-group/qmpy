from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from collections import *
from qmpy import INSTALL_PATH
from qmpy.models import *
from qmpy.io import write
from ..tools import get_globals
from configuration.vasp_settings import POTENTIALS

import pprint

def chem_pot_view(request):
    data = get_globals()

    chem_pots = defaultdict(lambda: defaultdict(dict))
    fits = []

    for fit in Fit.objects.all():
        fits.append(fit.name)
        for elt, mu in fit.mus.items():
            chem_pots[elt]['fits'][fit.name] = mu

    pot_set = POTENTIALS['vasp_rec']
    for elt in chem_pots:
        chem_pots[elt]['vasp'] = pot_set['elements'].get(elt, '')

    for elt, data in chem_pots.items():
        chem_pots[elt] = dict(data)
    chem_pots = dict(chem_pots)
    
    data['chem_pots'] = chem_pots
    data['fits'] = fits
    data['elements'] = sorted(data['chem_pots'].keys(), key=
            lambda x: elements[x]['z'])

    return render_to_response('materials/chem_pots.html', 
            data,
            RequestContext(request))

