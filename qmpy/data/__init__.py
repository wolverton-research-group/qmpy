import yaml
import os.path

location = os.path.dirname(__file__)

element_groups = {}
element_groups_file = os.path.join(location, 'elements', 'groups.yml')
if os.path.exists(element_groups_file):
    with open(element_groups_file, 'r') as fr:
        data = fr.read()
        element_groups = yaml.load(data)

elements = {}
elements_data_file = os.path.join(location, 'elements', 'data.yml')
if os.path.exists(elements_data_file):
    with open(elements_data_file, 'r') as fr:
        data = fr.read()
        elements = yaml.load(data)

chem_pots = {}
chem_pots_file = os.path.join(location, 'elements', 'chemical_potentials.yml')
if os.path.exists(chem_pots_file):
    with open(chem_pots_file, 'r') as fr:
        data = fr.read()
        chem_pots = yaml.load(data)

def save_chem_pots(chem_pots):
    with open(chem_pots_file, 'w') as fw:
        fw.write(yaml.dump(chem_pots, default_flow_style=False))
