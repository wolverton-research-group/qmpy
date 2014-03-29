import ConfigParser
import json
from qmpy import INSTALL_PATH
from qmpy.computing.resources import Host, Account, Project, Allocation, User
from qmpy.configuration.resources import *

config = ConfigParser.ConfigParser()
config.read(INSTALL_PATH+'/configuration/site.cfg')

VASP_POTENTIALS = config.get('VASP', 'potential_path')

def sync_resources():
    for host, data in hosts.items():
        h = Host.get(host)
        h.__dict__.update({'check_queue':data['check_queue'],
            'ip_address':data['ip_address'],
            'binaries':data['binaries'],
            'ppn':data['ppn'],
            'nodes':data['nodes'],
            'walltime':data['walltime'],
            'sub_script':data['sub_script'],
            'sub_text':data['sub_text']})
        h.save()

    for username, data in users.items():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
        user.save()

        for host, adata in data.items():
            host = Host.get(host)
            host.save()
            acc = Account.get(user, host)
            acc.__dict__.update(**adata)
            acc.save()

    for allocation, data in allocations.items():
        host = Host.get(data['host'])
        host.save()
        alloc = Allocation.get(allocation)
        alloc.host_id = host
        alloc.key = data.get('key', '')
        if alloc.key is None:
            alloc.key = ''
        alloc.save()
        for user in data['users']:
            user = User.objects.get_or_create(username=user)[0]
            user.save()
            alloc.users.add(user)

    for project, data in projects.items():
        proj = Project.get(project)
        proj.save()

        for user in data['users']:
            user = User.objects.get_or_create(username=user)[0]
            user.save()
            proj.users.add(user)

        for allocation in data['allocations']:
            alloc = Allocation.get(allocation)
            alloc.save()
            proj.allocations.add(alloc)
