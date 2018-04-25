from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *
from ..tools import get_globals

def get_marked_list(qs1, qs2):
    items = list(qs2)
    sub = list(qs1)
    for i in items:
        if i in qs1:
            i.included = True
        else:
            i.included = False
    return items

def construct_flot(phase_dict):
    data = []
    for p, v in phase_dict.items():
        series = {'label':p, 'data':v}
        data.append(series)
    return json.dumps(data)

def host_view(request, host_id):
    host = Host.objects.get(name=host_id)
    if request.method == 'POST':
        p = request.POST
        if not 'active' in p:
            host.state = -2
        else:
            host.state = 1
        host.save()
    data = {'host':host}
    return render_to_response('computing/host.html', 
            get_globals(data), 
            RequestContext(request))

def allocation_view(request, allocation_id):
    alloc = Allocation.objects.get(name=allocation_id)

    if request.method == 'POST':
        p = request.POST

        users = [ k.split('_')[1] for k in p.keys() if 'user_' in k 
                                        and p.get(k) == 'on' ]
        alloc.users = [ User.get(u) for u in users ]

        projects = [ k.split('_')[1] for k in p.keys() if 'project_' in k and 
                                                p.get(k) == 'on' ]
        alloc.project_set = projects

    users = get_marked_list(alloc.users.all(), User.objects.all())
    projects = get_marked_list(alloc.project_set.all(), Project.objects.all())

    data = {'allocation': alloc,
            'users': users,
            'projects': projects}
    return render_to_response('computing/allocation.html', 
            get_globals(data), 
            RequestContext(request))

def project_view(request, project_id):
    proj = Project.get(project_id)
    chart = {'running': proj.running.count(), 
             'completed': proj.completed.count(),
             'failed': proj.failed.count(),
             'held': proj.held.count(),
             'waiting': proj.waiting.count()}
    upcoming = proj.waiting
    if chart['waiting'] > 20:
        upcoming = upcoming[:20]

    if request.method == 'POST':
        p = request.POST
        if 'reset' in p:
            task_id = p.get('reset')
            task = Task.objects.get(id=task_id)
            for j in task.jobs:
                if j.state == 0:
                    j.delete()
            task.state = 0
            task.save()
            logger.info("Web reset: Task {}".format(task.id))
        elif 'restartall' in p:
            for t in proj.running:
                if t.last_job_state != 1:
                    for j in t.jobs:
                        if j.state == 0:
                            j.delete()
                    t.state = 0
                    t.save()
                    logger.info("Web reset: Task {}".format(t.id))
        else:
            if not 'active' in p:
                proj.state = -2
            else:
                proj.state = 1
            proj.priority = p.get('priority', 50)
            proj.save()

            allocs = [ k.split('_')[1] for k in p.keys() if 'alloc_' in k and
                                                        p.get(k) == 'on' ]
            proj.allocations = allocs 

            users = [ k.split('_')[1] for k in p.keys() if 'user_' in k and
                                                       p.get(k) == 'on']
            proj.users = [ User.get(u) for u in users ]

    allocs = get_marked_list(proj.allocations.all(), Allocation.objects.all())
    users = get_marked_list(proj.users.all(), User.objects.all())

    data = {'project': proj,
            'allocations': allocs, 
            'users': users,
            'plot': construct_flot(chart),
            'upcoming': upcoming}
    return render_to_response('computing/project.html', 
            get_globals(data), 
            RequestContext(request))

def user_view(request, user_id):
    data = {'user': User.objects.get(username=user_id)}
    return render_to_response('computing/user.html', 
            get_globals(data), 
            RequestContext(request))

def projects_view(request):
    projects = list(Project.objects.all())
    for p in projects:
        chart = {'running': p.running.count(),
                 'completed': p.completed.count(),
                 'held': p.held.count(),
                 'failed': p.failed.count(),
                 'waiting': p.waiting.count()}
        p.flot = construct_flot(chart)
    data = {'projects':projects}
    return render_to_response('computing/projects.html', 
            get_globals(data), 
            RequestContext(request))

def hosts_view(request):
    data = {'hosts': Host.objects.all()}
    return render_to_response('computing/hosts.html', 
            get_globals(data), 
            RequestContext(request))

def project_state_view(request, state=0, project_id=None):
    data = get_globals()
    project = Project.get(project_id)
    if isinstance(state, basestring):
        if state.lower() == 'held':
            state = -2
        elif state.lower() == 'failed':
            state = -1
        elif state.lower() == 'waiting':
            state = 0
        elif state.lower() == 'running':
            state = 1
        elif state.lower() == 'completed':
            state = 2

    tasks = project.task_set.filter(state=state)

    if state == 0:
        data['sname'] = 'Waiting'
    elif state == -1:
        data['sname'] = 'Failed'
    elif state == 1:
        data['sname'] = 'Running'
    elif state == 2:
        data['sname'] = 'Completed'
    elif state == -2:
        data['sname'] = 'Held'

    data['project'] = project
    data['tasks'] = tasks

    if request.method == 'POST':
        p = request.POST
        if 'reset' in p:
            task_id = p.get('reset')
            t = Task.objects.get(id=task_id)
            en = t.entry
            en.reset()
            logger.info("Web reset: Entry {}".format(en.id))

    return render_to_response('computing/project_state.html', 
            data, 
            RequestContext(request))

