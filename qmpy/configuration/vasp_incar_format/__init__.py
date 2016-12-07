import yaml
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
incar_tags_file = os.path.join(current_dir, 'incar_tag_groups.yml')
with open(incar_tags_file, 'r') as fr:
    VASP_INCAR_TAGS = yaml.load(fr)
