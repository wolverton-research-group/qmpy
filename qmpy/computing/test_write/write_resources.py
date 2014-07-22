from qmpy import *
import numbers

######
# headers for various configuration files
######

hosts_header = """#name:
#  binaries: {bin_name: /path/to/bin, dict: /of/such/pairs}
#  check_queue: /full/path/to/showq
#  hostname: full.host.name
#  ip_address: ###.###.##.###
#  nodes: # of nodes on machine
#  ppn: # of processors per node
#  sub_script: /full/path/to/submission/command
#  sub_text: filename for qfile to use a template. 
#            A file named "filename" must be in configuration/qfiles
#  walltime: maximum walltime, in seconds
"""
f_hosts = open("hosts.yml", 'w')
f_hosts.write(hosts_header)
f_hosts.write('\n')

users_header = """#name:
# hostname: {run_path:/where/to/run/on/host, username: usernameonhost}
# hostname1: {run_path:/where/to/run/on/host1, username: usernameonhost1}
# hostname2: {run_path:/where/to/run/on/host2, username: usernameonhost2}
# hostname3: {run_path:/where/to/run/on/host3, username: usernameonhost3}
"""
f_users = open("users.yml", 'w')
f_users.write(users_header)
f_users.write('\n')

allocations_header = """#name:
# host: hostname
# key: key needed for identifying allocation
# users: [list, of, permitted, users]
"""
f_allocations = open("allocations.yml", 'w')
f_allocations.write(allocations_header)
f_allocations.write('\n')

projects_header = """#name:
#  allocations: [list, of, alloctions, for, project]
#  priority: Base priority for the project. Lower numbers will be done soonest.
#  users: [list, of, allowed, users]
"""
f_projects = open("projects.yml", 'w')
f_projects.write(projects_header)
f_projects.write('\n')

######
# list of values that need to be written into the configuration files
######

host_values = ['binaries', 'check_queue', 'hostname', 'ip_address', \
        'nodes', 'ppn', 'sub_script', 'sub_text', 'walltime']

user_values = ['run_path', 'username']

allocation_values = ['host', 'key', 'users']

project_values = ['allocations', 'priority', 'users']

######
# a function to 'clean' the values from type unicode/ long/ etc. to string/ int
######
def clean(val):
    if isinstance(val, unicode):
        val = str(val)
    elif isinstance(val, numbers.Number):
        val = int(val)
    return val
 
######
# write host configurations into hosts.yml
######

hosts = Host.objects.all()
dict1 = {}
for h in hosts:
    dict2 = {}
    for hv in host_values:
        dict2[hv] = clean(h.__getattribute__(hv))
    dict1[clean(h.name)] = dict2
yaml.dump(dict1, f_hosts, default_flow_style=False)

######
# write user configurations into users.yml
######

users = User.objects.all()
dict1 = {}
for u in users:
    dict2 = {}
    accounts = Account.objects.filter(user=u)
    for a in accounts:
        dict2[clean(a.host.name)] = {'run_path':clean(a.run_path), \
                                    'username':clean(a.username)}
    dict1[clean(u.username)] = dict2
yaml.dump(dict1, f_users, default_flow_style=False)

######
# write allocation configurations into allocations.yml
######

alloc = Allocation.objects.all()
dict1 = {}
for a in alloc:
    dict2 = {}
    dict2['host'] =  clean(a.host.name)
    dict2['key'] = clean(a.key)
    dict2['users'] = [ clean(u) for u in a.users.all().values_list('username', flat=True) ]
    dict1[clean(a.name)] = dict2
yaml.dump(dict1, f_allocations, default_flow_style=False)

######
# write project configurations into projects.yml
######

pro = Project.objects.all()
dict1 = {}
for p in pro:
    dict2 = {}
    dict2['allocations'] = [ clean(a) for a in p.allocations.all().values_list('name', flat=True) ]
    dict2['priority'] = clean(p.priority)
    dict2['users'] = [ clean(u) for u in p.users.all().values_list('username', flat=True) ]
    dict1[clean(p.name)] = dict2
yaml.dump(dict1, f_projects, default_flow_style=False)

