import os, os.path
import yaml

vs_path = os.path.dirname(os.path.abspath(__file__))
VASP_SETTINGS = {}
for f in os.listdir(vs_path):
    if not 'yml' in f:
        continue
    settings =  yaml.load(open('%s/%s' % (vs_path, f)).read())
    VASP_SETTINGS[f.replace('.yml','')] = settings
