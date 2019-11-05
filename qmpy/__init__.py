# qmpy/__init__.py

"""
qmpy is a package containing many tools for computational materials science. 
"""

import numpy as np
try:
    import pyximport; pyximport.install()
except ImportError:
    pass
import logging
import logging.handlers
import os, os.path
import stat
import sys
import ConfigParser

import django.core.exceptions as de


with open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')) as fr:
    __version__ = fr.read().strip()
VERSION = __version__
__short_version__ = __version__.rpartition('.')[0]


INSTALL_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.join(INSTALL_PATH, 'qmpy', 'db')] + sys.path

LOG_PATH = os.path.join(INSTALL_PATH, 'logs')

config = ConfigParser.ConfigParser()
config.read(os.path.join(INSTALL_PATH,'configuration','site.cfg'))

VASP_POTENTIALS = config.get('VASP', 'potential_path')

if not os.path.exists(LOG_PATH):
    oldmask = os.umask(666)
    os.mkdir(LOG_PATH)
    os.umask(oldmask)

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

logfile = os.path.join(LOG_PATH, 'qmpy.log')
general = logging.handlers.WatchedFileHandler(logfile)
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
    import spglib 
    FOUND_SPGLIB = True
except ImportError:
    logging.warn("Failed to import spglib."
            'Download at: http://sourceforge.net/projects/spglib/ and'
            'follow instructions for installing python API')
    FOUND_SPGLIB = False

try:
    import sklearn
    FOUND_SKLEARN = True
except ImportError:
    FOUND_SKLEARN = False

### Kludge to get the django settings module into the path
sys.path.insert(-1, INSTALL_PATH)
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'qmpy.db.settings'

# Load models (Django >= 1.7)
try:
    import django
    django.setup()
except:
    pass

from models import *
from analysis import *
from analysis.thermodynamics import *
from analysis.symmetry import *
from analysis.vasp import *
from computing import *
from data import *

import yaml
import os

def read_spacegroups(numbers=None):
    data = open(INSTALL_PATH+'/data/spacegroups.yml').read()
    Spacegroup.objects.all().delete()
    spacegroups = yaml.safe_load(data)
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
    elts = []
    for elt, data in yaml.safe_load(elements).items():
        e = Element()
        e.__dict__.update(data)
        elts.append(e)
    Element.objects.bulk_create(elts)

def read_hubbards():
    hubs = open(INSTALL_PATH+'/configuration/vasp_settings/hubbards.yml').read()

    for group, hubbard in yaml.safe_load(hubs).items():
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
                except Exception:
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


# Try to prevent exception when importing before database is set up
try:
    if not Spacegroup.objects.exists():
        read_spacegroups()

    if not Element.objects.exists():
        read_elements()

    if not Potential.objects.exists():
        read_potentials()

    if not Hubbard.objects.exists():
        read_hubbards()

    if not User.objects.exists():
        sync_resources()

    if MetaData.objects.filter(type='global_warning').exists:
        for md in MetaData.objects.filter(type='global_warning'):
            logger.warn(md.value)
    if MetaData.objects.filter(type='global_info').exists:
        for md in MetaData.objects.filter(type='global_info'):
            logger.info(md.value)
except:
    pass
