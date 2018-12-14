import yaml
import os.path


this_dir = os.path.dirname(os.path.abspath(__file__))


element_groups = {}
element_groups_file = os.path.join(this_dir, 'elements', 'groups.yml')
if os.path.exists(element_groups_file):
    with open(element_groups_file, 'r') as fr:
        element_groups = yaml.load(fr)


elements = {}
elements_data_file = os.path.join(this_dir, 'elements', 'data.yml')
if os.path.exists(elements_data_file):
    with open(elements_data_file, 'r') as fr:
        elements = yaml.load(fr)


chem_pots = {}
chem_pots_file = os.path.join(this_dir, 'elements', 'chemical_potentials.yml')
if os.path.exists(chem_pots_file):
    with open(chem_pots_file, 'r') as fr:
        chem_pots = yaml.load(fr)


def save_chem_pots(chem_pots):
    with open(chem_pots_file, 'w') as fw:
        yaml.dump(chem_pots, fw, default_flow_style=False)
