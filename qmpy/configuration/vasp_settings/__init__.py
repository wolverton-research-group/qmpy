import yaml
import os
from inputs import *


this_dir = os.path.dirname(os.path.abspath(__file__))


# Read in Hubbard-U values
with open(os.path.join(this_dir, 'hubbards.yml'), 'r') as fr:
    thubbards = yaml.load(fr)

hubbards = {}
for setting, data in thubbards.items():
    hubbards[setting] = {}
    for k, v in data.items():
        elt, lig, ox = k.split('_')
        if ox == '*':
            hubbards[setting][(elt, lig, None)] = v
        else:
            hubbards[setting][(elt, lig, float(ox))] = v
HUBBARDS = hubbards


# Read in VASP pseudopotentials choices/labels
with open(os.path.join(this_dir, 'potentials.yml'), 'r') as fr:
    POTENTIALS = yaml.load(fr)

