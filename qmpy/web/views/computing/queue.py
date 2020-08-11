from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *
from qmpy.utils import *

import datetime
import os
import glob
import zipfile

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
    running = Job.objects.filter(state=1).order_by('-created')

    recent_ = Calculation.objects.filter(label='static',converged=True).order_by('-id')[:25]

    recent_name_dict = dict([(str(c.entry.id), format_html(c.comp)) for c in recent_])
    recent_finished_dict = dict([(str(c.entry.id), c.entry.task_set.order_by('-finished')[0].finished) for c in recent_])
    recent_project_dict = dict([(str(c.entry.id), 
                                 ', '.join(p.name for p in c.entry.task_set.order_by('-finished')[0].projects)) 
                                for c in recent_])

    recent_ids = list(map(lambda x: x[0], sorted(recent_finished_dict.items(), key=lambda x: x[1],
                                                 reverse=True)))
    count = running.count()

    data = {'running':running[:20],
            'count':count,
            'recent_name_dict': recent_name_dict,
            'recent_finished_dict': recent_finished_dict,
            'recent_project_dict': recent_project_dict,
            'recent_ids':recent_ids,
           }

    data.update(csrf(request))
    return render_to_response('computing/queue.html', 
            data, 
            RequestContext(request))

def online_view(request):
    data = {'running':1,
            'upcoming':1}
    if request.method == 'POST':
        rf = request.FILES
        if 'myfilesingle' in rf:
            fl = request.FILES['myfilesingle']
            folder = os.path.join('/','home', 'oqmd', 'libraries', 'Online_submit', datetime.datetime.now().strftime("%h-%d-%Y-%H-%M-%S"))
            if not os.path.exists(folder):
                os.mkdir(folder)
            with open(os.path.join(folder, "POSCAR"), 'w') as f:
                for c in fl.chunks():
                    f.write(c)
            return render_to_response('computing/online_submit.html', 
                    {'uploaded_url': os.path.join(folder, 'POSCAR')}, 
                    RequestContext(request))

        rp = request.POST
        if 'subjobs' in rp:
            proj = Project.get('Online_submit')
            folder = os.path.join('/','home', 'oqmd', 'libraries', 'Online_submit')
            poscars = glob.glob(os.path.join(folder,'*','POSCAR'))

            with open(os.path.join(folder, 'sub_log'), 'r') as sub_log_f:
                sub_lst = []
                for l in sub_log_f:
                    sub_lst.append(l.strip())

            with open(os.path.join(folder, 'dup_log'), 'r') as dup_log_f:
                dup_lst = []
                for l in dup_log_f:
                    dup_lst.append(l.strip())

            sub_new = open(os.path.join(folder, 'sub_log_new'), 'w')
            dup_new = open(os.path.join(folder, 'dup_log_new'), 'w')

            for poscar in poscars:
                if poscar in sub_lst:
                    sub_new.write(poscar+"\n")
                    continue

                if poscar in dup_lst:
                    dup_new.write(poscar+"\n")
                    continue
                
                try:
                    en = Entry.create(poscar, projects=[proj], keywords=['Online_submit'])
                except:
                    dup_new.write(poscar+"\n")
                    continue

                if en.holds:
                    dup_new.write(poscar+"\n")
                    continue

                en.save()
                if en.tasks:
                    continue
                
                task = Task.create(en, 'static', priority=1)
                task.save()
                sub_new.write(poscar+'\n')

            sub_new.close()
            dup_new.close()
            os.rename(os.path.join(folder,'sub_log_new'), 
                      os.path.join(folder,'sub_log'))
            os.rename(os.path.join(folder,'dup_log_new'), 
                      os.path.join(folder,'dup_log'))
                                      
    return render_to_response('computing/online_submit.html', 
            data, 
            RequestContext(request))
