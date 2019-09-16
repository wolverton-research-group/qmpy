import yaml
import os
loc = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(loc, 'hosts.yml'), 'r') as fr:
    try:
        hosts = yaml.load(fr,Loader=yaml.FullLoader)
    except:
        hosts = yaml.load(fr)

with open(os.path.join(loc, 'projects.yml'), 'r') as fr:
    try:
        projects = yaml.load(fr,Loader=yaml.FullLoader)
    except:
        projects = yaml.load(fr)

with open(os.path.join(loc, 'allocations.yml'), 'r') as fr:
    try:
        allocations = yaml.load(fr,Loader=yaml.FullLoader)
    except:
        allocations = yaml.load(fr)

with open(os.path.join(loc, 'users.yml'), 'r') as fr:
    try:
        users = yaml.load(fr,Loader=yaml.FullLoader)
    except:
        users = yaml.load(fr)
