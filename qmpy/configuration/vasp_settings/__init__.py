import yaml
import os, os.path
from inputs import *
from qmpy import INSTALL_PATH

vs_path = os.path.dirname(os.path.abspath(__file__))
try:
    thubbards = yaml.load(open(vs_path+'/hubbards.yml').read(),Loader=yaml.FullLoader)
except:
    thubbards = yaml.load(open(vs_path+'/hubbards.yml').read())
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
try:
    POTENTIALS = yaml.load(open(vs_path+'/potentials.yml').read(),Loader=yaml.FullLoader)
except:
    POTENTIALS = yaml.load(open(vs_path+'/potentials.yml').read())
