import numpy as np
import pyximport; pyximport.install()
import logging
import logging.handlers
import os
from os.path import dirname, abspath
import sys
import re
import ConfigParser

INSTALL_PATH = abspath(dirname(__file__))
LOG_PATH = INSTALL_PATH+'/logs/'

config = ConfigParser.ConfigParser()
config.read(INSTALL_PATH+'/configuration/site.cfg')

VASP_POTENTIALS = config.get('VASP', 'potential_path')

if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# the default log level for normal loggers
logLevel = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)

FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
FORMAT_SHORT = '%(levelname)-8s %(message)s'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(FORMAT, TIME_FORMAT)
short_formatter = logging.Formatter(FORMAT_SHORT)
console = logging.StreamHandler()
console.setFormatter(short_formatter)

# uncomment to set debugging output for all normal loggers
#console.setLevel(logging.DEBUG)

general = logging.handlers.WatchedFileHandler(LOG_PATH+'qmpy.log')
general.setFormatter(formatter)

logger.addHandler(general)
logger.addHandler(console)

class qmpyBaseError(Exception):
    """Baseclass for qmpy Exceptions"""

try:
    import ase
    FOUND_ASE = True
except ImportError:
    FOUND_ASE = False
    logging.warn('Failed to import ASE')

try:
    import pulp
    FOUND_PULP = True
except ImportError:
    FOUND_PULP = False
    logging.warn('Failed to import PuLP')

try:
    import matplotlib
    FOUND_MPL = True
except ImportError:
    FOUND_MPL = False
    logging.warn('Failed to import matplotlib')

try:
    import pyspglib 
    FOUND_SPGLIB = True
except ImportError:
    FOUND_SPGLIB = False

### Kludge to get the django settings module into the path
sys.path.insert(-1, INSTALL_PATH)
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'qmpy.db.settings'

from models import *
from analysis import *
from analysis.thermodynamics import *
from analysis.symmetry import *
from analysis.vasp import *
from computing import *
from data import *

import yaml
import os

from qmpy import INSTALL_PATH
from qmpy.configuration import VASP_POTENTIALS, sync_resources
from qmpy.models import *

def read_spacegroups(numbers=None):
    data = open(INSTALL_PATH+'/data/spacegroups.yml').read()
    Spacegroup.objects.all().delete()
    spacegroups = yaml.load(data)
    for sgd in spacegroups.values():
        if numbers:
            if sgd['number'] not in numbers:
                continue
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
    if not VASP_POTENTIALS:
        return
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


def sync_resources():
    for host, data in hosts.items():
        h = Host.get(host)
        h.__dict__.update({'check_queue':data['check_queue'],
            'ip_address':data['ip_address'],
            'binaries':data['binaries'],
            'ppn':data['ppn'],
            'nodes':data['nodes'],
            'walltime':data['walltime'],
            'sub_script':data['sub_script'],
            'sub_text':data['sub_text']})
        h.save()

    for username, data in users.items():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
        user.save()

        for host, adata in data.items():
            host = Host.get(host)
            host.save()
            acc = Account.get(user, host)
            acc.__dict__.update(**adata)
            acc.save()

    for allocation, data in allocations.items():
        host = Host.get(data['host'])
        host.save()
        alloc = Allocation.get(allocation)
        alloc.host_id = host
        alloc.key = data.get('key', '')
        if alloc.key is None:
            alloc.key = ''
        alloc.save()
        for user in data['users']:
            user = User.objects.get_or_create(username=user)[0]
            user.save()
            alloc.users.add(user)

    for project, data in projects.items():
        proj = Project.get(project)
        proj.save()

        for user in data['users']:
            user = User.objects.get_or_create(username=user)[0]
            user.save()
            proj.users.add(user)

        for allocation in data['allocations']:
            alloc = Allocation.get(allocation)
            alloc.save()
            proj.allocations.add(alloc)

if not Spacegroup.objects.exists():
    read_spacegroups()

if not Element.objects.exists():
    read_elements()

if not Potential.objects.exists():
    read_potentials()

if not Hubbard.objects.exists():
    read_hubbards()
