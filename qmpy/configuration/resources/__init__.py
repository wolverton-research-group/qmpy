import os
import yaml


this_dir = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(this_dir, 'hosts.yml'), 'r') as fr:
    hosts = yaml.load(fr)

with open(os.path.join(this_dir, 'projects.yml'), 'r') as fr:
    projects = yaml.load(fr)

with open(os.path.join(this_dir, 'allocations.yml'), 'r') as fr:
    allocations = yaml.load(fr)

with open(os.path.join(this_dir, 'users.yml'), 'r') as fr:
    users = yaml.load(fr)
