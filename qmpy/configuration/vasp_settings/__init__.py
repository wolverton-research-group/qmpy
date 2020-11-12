import yaml
import os, os.path
from .inputs import *
from qmpy import INSTALL_PATH

vs_path = os.path.dirname(os.path.abspath(__file__))
thubbards = yaml.safe_load(open(vs_path + "/hubbards.yml").read())
hubbards = {}
for setting, data in list(thubbards.items()):
    hubbards[setting] = {}
    for k, v in list(data.items()):
        elt, lig, ox = k.split("_")
        if ox == "*":
            hubbards[setting][(elt, lig, None)] = v
        else:
            hubbards[setting][(elt, lig, float(ox))] = v

HUBBARDS = hubbards
POTENTIALS = yaml.safe_load(open(vs_path + "/potentials.yml").read())
