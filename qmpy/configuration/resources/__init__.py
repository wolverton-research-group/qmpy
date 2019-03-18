import yaml
import os
loc = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(loc, 'hosts.yml'), 'r') as fr:
    hosts = yaml.load(fr)

with open(os.path.join(loc, 'projects.yml'), 'r') as fr:
    projects = yaml.load(fr)

with open(os.path.join(loc, 'allocations.yml'), 'r') as fr:
    allocations = yaml.load(fr)

with open(os.path.join(loc, 'users.yml'), 'r') as fr:
    users = yaml.load(fr)
