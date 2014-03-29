import yaml
import os

from qmpy import INSTALL_PATH
from qmpy.configuration import VASP_POTENTIALS, sync_resources
from qmpy.models import *

sync_resources()

def read_spacegroups():
    data = open(INSTALL_PATH+'/data/spacegroups.yml').read()
    Spacegroup.objects.all().delete()
    spacegroups = yaml.load(data)
    for sgd in spacegroups.values():
        sg = Spacegroup(number=sgd['number'],
                        hm=sgd['hm'],
                        hall=sgd['hall'],
                        schoenflies=sgd['schoenflies'],
                        lattice_system=sgd['system'])
        sg.save()
        cvs = []
        for cv in sgd['centering_vectors']:
            cvs.append(Translation.get(cv))
        sg.centering_vectors = cvs

        ops = []
        for op in sgd['sym_ops']:
            ops.append(Operation.get(','.join(op)))
        sg.sym_ops = ops
        sg.save()

        wycks = []
        for k, site in sgd['wyckoff_sites'].items():
            wycks.append(WyckoffSite(symbol=k, 
                               x=site['coordinate'].split()[0],
                               y=site['coordinate'].split()[1],
                               z=site['coordinate'].split()[2],
                               multiplicity=site['multiplicity']))
        sg.site_set = wycks

def read_elements():
    elements = open(INSTALL_PATH+'/data/elements/data.yml').read()
    Element.objects.all().delete()

    for elt, data in yaml.load(elements).items():
        e = Element(**data)
        e.save()

def read_hubbards():
    hubs = open(INSTALL_PATH+'/configuration/vasp_settings/hubbards.yml').read()

    for group, hubbard in yaml.load(hubs).items():
        for ident, data in hubbard.items():
            elt, ligand, ox = ident.split('_')
            hub = Hubbard(
                    l=data['L'],
                    u=data['U'])
            if ox != '*':
                hub.ox = ox
            hub.ligand_id = ligand
            hub.element_id = elt
            hub.convention = group
            hub.save()

def read_potentials():
    loaded = []
    for (path, dirs, files) in os.walk(VASP_POTENTIALS):
        for f in files:
            if 'GW' in path:
                continue
            if 'POTCAR' in files and not path in loaded:
                loaded.append(path)
                try:
                    pots = Potential.read_potcar(path+'/POTCAR')
                    for pot in pots:
                        pot.save()
                except Exception, err:
                    print 'Couldn\'t load:', path

