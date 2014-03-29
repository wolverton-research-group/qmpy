from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *

def task_view(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':
        for j in task.jobs.filter(state=1):
            j.collect()
        task.state = -2
        task.save()
    data = {'task':task}
    return render_to_response('computing/task.html', 
            data, 
            RequestContext(request))

def job_view(request, job_id):
    job = Job.objects.get(id=job_id)
    in_dir, stdout = ('', '')
    if job.state == 1:
        in_dir = job.account.execute('ls %s' % (job.run_path))
        stdout = job.account.execute('cat %s/stdout.txt' % (job.run_path))
    data = {'job': job,
            'files': in_dir,
            'stdout': stdout}
    if request.method == 'POST':
        job.collect()
        data.update(csrf(request))
    return render_to_response('computing/job.html', 
            data, 
            RequestContext(request))

def queue_view(request):
    upcoming = {}
    running = Job.objects.filter(state=1)
    for p in Project.objects.all():
        uc = p.task_set.filter(state=0).order_by('priority').select_related()[:20]
        if uc.exists():
            upcoming[p.name] = list(uc)
    if request.method == 'POST':

        for job in running:
            job.collect()
    data = {'running':running,
            'upcoming':upcoming}
    data.update(csrf(request))
    return render_to_response('computing/queue.html', 
            data, 
            RequestContext(request))
