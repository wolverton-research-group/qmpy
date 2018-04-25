#!/usr/bin/env python

from django.db import models
import json
import os.path
import time
from datetime import datetime, timedelta
import random

from resources import Project, Account, Allocation
from qmpy.analysis.vasp import Calculation
from qmpy.db.custom import *
import qmpy

class TaskError(Exception):
    """A project was needed but not provided"""

class ResourceUnavailableError(Exception):
    """Resource is occupied"""

class Task(models.Model):
    """
    Model for a :Task: to be done. 
    
    A :Task: consists of a module, which is the name 
    of a computing script, and a set of keyword arguments, specified as a
    dictionary as the `kwargs` attribute of the task. In order for a Task for
    be completed, it must also be assigned one or more :Project:s.

    Relationships:
        | :mod:`~qmpy.Entry` via entry
        | :mod:`~qmpy.Job` via job_set
        | :mod:`~qmpy.Project` via project_set

    Attributes:
        | id
        | created: datetime object for when the task was created.
        | finished: datetime object for when the task was completed.
        | module: The name of a function in :mod:`~qmpy.computing.scripts`  
        | kwargs: dict of keyword:value pairs to pass to the calculation
        |   module.
        | priority: Priority of the task. Lower values are more urgent. 
        | state: State code, given by the table below.

    Task codes:

    +------+-------------------+
    | Code | Description       |
    +======+===================+
    | -2   | being held        |
    +------+-------------------+
    | -1   | encountered error |
    +------+-------------------+
    |  0   | ready to run      |
    +------+-------------------+
    |  1   | jobs running      |
    +------+-------------------+
    |  2   | completed         |
    +------+-------------------+

    """
    module = models.CharField(max_length=60)
    kwargs = DictField()
    state = models.IntegerField(default=0)
    priority = models.IntegerField(default=50)
    created = models.DateTimeField(blank=True, auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    entry = models.ForeignKey('Entry')
    project_set = models.ManyToManyField(Project)

    _projects = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'tasks'

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        self.project_set = [ Project.get(p) for p in self.projects ]

    @property
    def projects(self):
        """List of related projects."""
        if self._projects is None:
            self._projects = list(self.project_set.all())
        return self._projects

    @projects.setter
    def projects(self, projects):
        self._projects = projects

    def get_project(self):
        projects = self.project_set.filter(state=1)
        projects = [ p for p in projects if p.active ]
        if not projects:
            return
        return random.choice(projects)

    @property
    def eligible_to_run(self):
        if self.state != 0:
            return False
        if self.entry.holds:
            return False
        return True

    @staticmethod
    def create(entry, module='static', kwargs={},
            priority=None, projects=None): 
        if projects is None:
            projects = entry.projects
        elif isinstance(projects, basestring):
            projects = Project.objects.get(name=projects)
        if priority is None:
            priority = len(entry.input)
        task, created = Task.objects.get_or_create(entry=entry, 
                kwargs=kwargs, module=module)
        if created:
            task.projects = projects
        else:
            task.projects += projects

        task.priority = priority
        return task

    def complete(self):
        """Sets the Task state to 2 and populates the finished field."""
        self.state = 2
        self.finished = datetime.now()

    def hold(self):
        self.state = -2

    def fail(self):
        self.state = -1

    def __str__(self):
        return '%s (%s: %s)' % (self.module, self.entry, self.entry.path)

    @property
    def jobs(self):
        """List of jobs related to the task."""
        return self.job_set.all()

    @property
    def last_job_state(self):
        if self.job_set.all():
            return self.job_set.all().order_by('-id')[0].state

    @property
    def errors(self):
        """List of errors encountered by related calculations."""
        return self.entry.errors

    def get_jobs(self, project=None, allocation=None, account=None, host=None):
        """
        Check the calculation module specified by the `Task`, and returns
        a list of :class:`Job` objects accordingly.

        Calls the task's entry's "do" method with the `Task.module` as the
        first argument, and passing `Task.kwargs` as keyword arguments. 

        Returns:
            List of Job objects. When nothing is left to do for the
            task, returns empty.

        Raises:
            ResourceUnavailableError:
                Raise if for the specified project, allocation, account and/or host
                there are no available cores.
        """
        if host != None:
            if not project:
                projects = self.project_set.filter(allocations__host=host, state=1)
                project = random.choice(list(projects))
            if not allocation:
                allocations = project.allocations.filter(host=host, state=1)
                allocation = random.choice(list(allocations))
        elif project != None:
            allocation = project.get_allocation()
            if not allocation:
                raise ResourceUnavailableError
        else:
            project = self.get_project()

        if account is None:
            if project is None:
                account = allocation.get_account()
            elif not allocation is None:
                account = allocation.get_account(users=list(project.users.all()))

        calc = self.entry.do(self.module, **self.kwargs)

        # Special case: Adjustments for certain clusters
        if not allocation is None:
            if allocation.name == 'b1004':
                # Can only run parallel VASP on b1004 allocation
                calc.instructions['serial'] = False
                calc.instructions['binary'] = 'vasp_53'
                calc.instructions['mpi'] = 'mpirun -machinefile $PBS_NODEFILE -np $NPROCS'

            if allocation.name == 'babbage':
                # Check if calculation is parallel
                if 'serial' in calc.instructions and not calc.instructions['serial']:
    
                    # Different MPI call on Babbage
                    calc.instructions['mpi'] = 'mpirun -np $NPROCS -machinefile $PBS_NODEFILE -tmpdir /scratch'
            if allocation.name == 'd20829':
                # Sheel doesn't have access to b1004 binaries
                calc.instructions['binary'] = '~/vasp_53'

        jobs = []
        #for calc in calcs:
        if calc.instructions:
            self.state = 1
            new_job = Job.create(
                task=self, 
                allocation=allocation, 
                account=account,
                entry=self.entry,
                **calc.instructions)
            jobs.append(new_job)
            calc.save()
        elif calc.converged:
            self.complete()
        else:
            self.state = -1
        return jobs

class Job(models.Model):
    """
    Base class for job submitted to a compute cluster.

    Relationships:
        | :mod:`~qmpy.Task` via task
        | :mod:`~qmpy.Account` via account. The account the calculation is
        |   performed on.
        | :mod:`~qmpy.Allocation` via allocation. The allocation on which the
        |   calculation is being performed.
        | :mod:`~qmpy.Entry` via entry

    Attributes:
        | id
        | created: datetime object for when the task was created.
        | finished: datetime object for when the task was completed.
        | ncpus: # of processors assigned.
        | path: Origination path of the calculation.
        | run_path: Path of the calculation on the compute resource.
        | qid: PBS queue ID number.
        | walltime: Max walltime (in seconds).
        | state: State code, defined as in the table below.

    Job codes

    +------+-------------------+
    | Code | Description       |
    +======+===================+
    | -1   | encountered error |
    +------+-------------------+
    |  0   | ready to submit   |
    +------+-------------------+
    |  1   | currently running |
    +------+-------------------+
    |  2   | completed         |
    +------+-------------------+

    """
    qid = models.IntegerField(default=0)
    walltime = models.DateTimeField(blank=True)
    path = models.CharField(max_length=200)
    run_path = models.CharField(max_length=200)
    ncpus = models.IntegerField(blank=True)
    created = models.DateTimeField(blank=True, auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(default=0)

    task = models.ForeignKey(Task)
    entry = models.ForeignKey('Entry')
    account = models.ForeignKey(Account)
    allocation = models.ForeignKey(Allocation)

    class Meta:
        app_label = 'qmpy'
        db_table = 'jobs'

    @staticmethod
    def create(task=None, allocation=None, entry=None,
            account=None,
            path=None, 
            walltime=3600, serial=None,
            header=None,
            mpi=None, binary=None, pipes=None,
            footer=None):

        if entry is None:
            entry = task.entry

        #assert isinstance(allocation, Allocation)
        #assert isinstance(task, Task)
        #assert path is not None

        #if account is None:
        #    account = allocation.get_account()
        
        job = Job(path=path, walltime=walltime, 
                allocation=allocation,
                account=account,
                entry=entry,
                task=task)

        #if walltime < 3600:
        #    nodes = 1
        #    ppn = int(walltime/3600.*job.account.host.ppn)
        #    walltime = walltime/ppn
        #else:
        #    ppn = job.account.host.ppn
        #    nodes = 1+int(walltime/float(job.account.host.walltime))
        #    walltime = walltime/float(ppn*nodes)
        
        if serial:
            ppn = 1
            nodes = 1
            walltime = 3600*24*4
            if job.allocation.name == 'p20746':
                walltime = 3600*24
            if job.allocation.name == 'p20747':
                walltime = 3600*24
        else:
            nodes = 1
            ppn = job.account.host.ppn
            walltime = job.account.host.walltime
            
        binary = job.account.host.get_binary(binary)
        if not binary:
            raise AllocationError

        sec = timedelta(seconds=walltime)
        d = datetime(1,1,1) + sec
        job.walltime = d
        walltime = '%02d:%02d:%02d:%02d' % (
                d.day-1, 
                d.hour, 
                d.minute,
                d.second)

        qp = qmpy.INSTALL_PATH + '/configuration/qfiles/'
        text = open(qp+job.account.host.sub_text+'.q', 'r').read()
        qfile = text.format(
                host=allocation.host.name,
                key=allocation.key, name=job.description,
                walltime=walltime, nodes=nodes, ppn=ppn,
                header=header,
                mpi=mpi, binary=binary, pipes=pipes,
                footer=footer)

        qf=open(job.path+'/auto.q', 'w')
        qf.write(qfile)
        qf.close()
        job.ncpus = ppn*nodes
        job.run_path = job.account.run_path+'/'+job.description
        return job

    @property
    def walltime_expired(self):
        from datetime import datetime, timedelta
        elapsed = datetime.now() - self.created
        if elapsed.total_seconds() > self.walltime:
            return True
        else:
            return False

    @property
    def calculation(self):
        try:
            return Calculation.objects.get(path=self.path)
        except:
            return

    @property
    def subdir(self):
        return self.path.replace(self.entry.path, '')

    @property
    def description(self):
        uniq = ''
        if self.task.kwargs:
            uniq='_' + '_'.join(['%s:%s' % (k, v) for k, v in self.task.kwargs.items()])
        return '{entry}_{subdir}{uniq}'.format(
                entry=self.entry.id,
                subdir=self.subdir.strip('/').replace('/','_'),
                uniq=uniq)

    def __str__(self):
        return '%s on %s' % (self.description, self.account)

    def is_done(self):
        # Ensure the calculation has had time to show up showq
        if datetime.now() + timedelta(seconds=-600) < self.created:
            return False

        # then check to see if it is still there
        if self.qid in self.account.host.running_now:
            return False
        else:
            return True

    def submit(self):
        if not self.account.host.active:
            return
        self.created = datetime.now()
        self.qid = self.account.submit(path=self.path,
                run_path=self.run_path,
                qfile='auto.q')
        self.task.state = 1
        self.state = 1

    def collect(self):
        self.task.state = 0
        self.task.save()
        self.state = 2
        self.account.copy(move=True,
                to='local', destination=self.path,
                folder=self.run_path, file='*')
        self.account.execute('rm -rf %s' % self.run_path, ignore_output=True)
        self.finished = datetime.now()
        self.save()
