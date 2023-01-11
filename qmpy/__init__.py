# qmpy/__init__.py

"""
qmpy is a package containing many tools for computational materials science.
"""
import numpy as np
import logging
import logging.handlers
import os
import yaml
import stat
import sys
import ConfigParser
import django.core.exceptions as de


##############################################################################
# Config files
# Try reading in the base config file and path to VASP pseudopotentials
##############################################################################

INSTALL_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.join(INSTALL_PATH, 'qmpy', 'db')] + sys.path

config = ConfigParser.ConfigParser()
config.read(os.path.join(INSTALL_PATH, 'configuration', 'site.cfg'))

# read in the location of the VASP Potential on the OQMD server
VASP_POTENTIALS = config.get('VASP', 'potential_path')



##############################################################################
# Logging
# Set path to the default log file, format for the logger, etc.
##############################################################################

LOG_PATH = os.path.join(INSTALL_PATH, 'logs')
if not os.path.exists(LOG_PATH):
    oldmask = os.umask(666)
    os.mkdir(LOG_PATH)
    os.umask(oldmask)

# the default log level for normal loggers
logLevel = logging.DEBUG

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



##############################################################################
# Imports
# Try importing essential packages and throw suitable warnings/exceptions
##############################################################################

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

# Use spglib versions >1.9.0
try:
    import spglib
    FOUND_SPGLIB = True
except ImportError:
    logging.warn("Failed to import spglib"
                 " (https://atztogo.github.io/spglib/python-spglib.html)")
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




##############################################################################
# Imports
# Imports from qmpy subpackages to remove relative imports
##############################################################################
from models import *
from analysis import *
from analysis.thermodynamics import *
from analysis.symmetry import *
from analysis.vasp import *
from computing import *
from data import *
from configuration.resources import *


def read_spacegroups(numbers=None, overwrite_existing=True):
    """
    read space group data: number, Hermann-Maguin notation, Hall number,
    Schonflies number, lattice system, symmetry operators, Wyckoff positions,
    for all the 230 space groups from 'INSTALL_PATH/data/spacegroups.yml'.
    """
    spg_datafile = os.path.join(INSTALL_PATH, 'data', 'spacegroups.yml')
    if not os.path.exists(spg_datafile):
        print('Space groups data file {} not found.'.format(spg_datafile))
        return

    Spacegroup.objects.all().delete()
    with open(spg_datafile, 'r') as fr:
        spacegroups = yaml.load(fr)

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
    """
    read elemental properties: atomic number, atomic weight, electronegativity,
    HHI index, etc. for all the elements from 'INSTALL_PATH/data/elements.yml'.
    """
    elem_datafile = os.path.join(INSTALL_PATH, 'data', 'elements', 'data.yml')
    if not os.path.exists(elem_datafile):
        sys.stdout.write('Elemental properties data not found.\n')
        return
    elements = open(elem_datafile).read()
    Element.objects.all().delete()
    elts = []
    for elt, data in yaml.load(elements).items():
        e = Element()
        e.__dict__.update(data)
        elts.append(e)
    Element.objects.bulk_create(elts)

def read_hubbards():
    """
    read Hubbard U values to be used for the suitable elements from the file
    'INSTALL_PATH/configuration/vasp_settings/hubbards.yml'
    """
    hubs_file = os.path.join(INSTALL_PATH, 'configuration', 'vasp_settings', 
                             'hubbards.yml')
    if not os.path.exists(hubs_file):
        sys.stdout.write('Hubbard data file not found.\n')
        return
    hubs = open(hubs_file).read()

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
    """
    read the VASP POTCAR files and store them in the database.
    """
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
                    pots = Potential.read_potcar(os.path.join(path, 'POTCAR'))
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
            print host, adata
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


##############################################################################
# Configuration files and pseudopotentials
##############################################################################

# Load models (Django >= 1.7)
try:
    import django
    django.setup()
except:
    pass

# Try to prevent exception when importing before database is set up
try:
    # read spacegroup data for all 230 spacegroups
    if not Spacegroup.objects.exists():
        read_spacegroups()

    # read elemental data like atomic number, density, etc. for all elements
    # the source, IIRC, is Mathematica
    if not Element.objects.exists():
        read_elements()

    # read in all the VASP Potentials
    if not Potential.objects.exists():
        read_potentials()

    # read in the Hubbard U values
    if not Hubbard.objects.exists():
        read_hubbards()

    # sync resources
    ###if not User.objects.exists():
    ###    sync_resources()

    # global_warning and global_info created to alert users, dispense info on
    # the OQMD website in the form of pagewidth-spanning banners
    if MetaData.objects.filter(type='global_warning').exists:
        for md in MetaData.objects.filter(type='global_warning'):
            logger.warn(md.value)

    if MetaData.objects.filter(type='global_info').exists:
        for md in MetaData.objects.filter(type='global_info'):
            logger.info(md.value)
except:
    pass
