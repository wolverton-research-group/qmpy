from django.http import HttpResponse
from django.shortcuts import render

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from qmpy import INSTALL_PATH
from qmpy.models import *
from .resources import *
from .queue import *
from .new import *

def icsd_progress():
    n = 60
    tasks = Task.objects.filter(project_set='icsd', entry__natoms__lte=n)

    data = tasks.values_list('entry__natoms', 'state')
    done = []
    failed = []
    idle = []
    running = []
    for task in data:
        if task[1] == 2:
            done.append(task[0])
        elif task[1] == 1:
            running.append(task[0])
        elif task[1] == 0:
            idle.append(task[0])
        elif task[1] == -1:
            failed.append(task[0])

    plt.hist([ done, running, failed, idle], histtype='barstacked',
            label=['done', 'running' ,'failed', 'waiting'],
            bins=n)#, cumulative=True)
    plt.legend(loc='best')

    plt.xlabel('# of atoms in primitive cell')
    plt.ylabel('# of entries')

    img = BytesIO()
    plt.savefig(img, dpi=75, bbox_inches='tight',format='png')
    img.seek(0)
    data_uri = img.getvalue()
    img.close()

    data_uri = base64.b64encode(data_uri)
    data_uri = data_uri.decode('utf-8')
    plt.close()
    return data_uri

def computing_view(request):
    data = {'jobs':Job.objects.filter(state=1),
            'hosts': Host.objects.all(),
            'users': User.objects.all(),
            'projects': Project.objects.all(),
            'allocations': Allocation.objects.all(),
            'icsd':icsd_progress()}
    return render(request,'computing/index.html', 
            data)

