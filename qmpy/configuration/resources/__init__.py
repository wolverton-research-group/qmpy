import yaml
import os, os.path
loc = os.path.dirname(os.path.abspath(__file__))

hosts = yaml.load(open(loc+'/hosts.yml'))
projects = yaml.load(open(loc+'/projects.yml'))
allocations = yaml.load(open(loc+'/allocations.yml'))
users = yaml.load(open(loc+'/users.yml'))
