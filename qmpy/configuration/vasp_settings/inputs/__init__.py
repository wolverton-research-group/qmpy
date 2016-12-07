import os
import glob
import yaml

vs_path = os.path.dirname(os.path.abspath(__file__))
VASP_SETTINGS = {}
for f in glob.glob(os.path.join(vs_path, '*.yml')):
    with open(f, 'r') as fr:
        settings =  yaml.load(fr.read())
    configuration = os.path.basename(f).strip('.yml')
    VASP_SETTINGS[configuration] = settings
