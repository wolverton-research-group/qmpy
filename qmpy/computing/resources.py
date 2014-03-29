from datetime import datetime, timedelta
import random
import subprocess
import os
import os.path
import time
from collections import defaultdict
import json
import logging

from django.db import models
from django.contrib.auth.models import AbstractUser

import qmpy
from qmpy.db.custom import DictField
import queue as queue

logger = logging.getLogger(__name__)

class AllocationError(Exception):
    """Problem with the allocation"""

class SubmissionError(Exception):
    """Failed to submit a job"""

class User(AbstractUser):
    """
    User model - stores an oqmd users information.

    Relationships:
        | :mod:`~qmpy.Account` via account_set
        | :mod:`~qmpy.Allocation` via allocation_set
        | :mod:`~qmpy.Project` via project_set

    Attributes:
        | id
        | username
        | first_name
        | last_name
        | date_joined
        | is_active
        | is_staff
        | is_superuser
        | last_login
        | email

    """

    class Meta:
        app_label = 'qmpy'
        db_table = 'users'

    @property
    def running(self):
        return queue.Job.objects.filter(account__user=self, state=1)

    @classmethod
    def get(cls, name):
        try:
            return cls.objects.get(username=name)
        except cls.DoesNotExist:
            return cls(username=name)

class Host(models.Model):
    """
    Host model - stores all host information for a cluster.

    Relationships:
        | account
        | allocation

    Attributes:
        | name: Primary key.
        | binaries: dict of label:path pairs for vasp binaries.
        | check_queue: Path to showq command
        | checked_time: datetime object for the last time the queue was 
        |   checked.
        | hostname: Full host name. 
        | ip_address: Full ip address.
        | nodes: Total number of nodes.
        | ppn: Number of processors per node.
        | running: dict of PBS_ID:state pairs.
        | sub_script: Path to qsub command
        | sub_text: Path to queue file template.
        | utilization: Number of active cores (based on showq).
        | walltime: Maximum walltime on the machine.
        | state: State code. 1=Up, 0=Full (auto-resets to 1 when jobs are
        |   collected), -1=Down.

    """
    name = models.CharField(max_length=63, primary_key=True)
    ip_address = models.IPAddressField(null=True)
    hostname = models.CharField(max_length=255)
    binaries = DictField()
    ppn = models.IntegerField(default=8)
    nodes = models.IntegerField(default=30)
    walltime = models.IntegerField(default=3600*24)
    sub_script = models.CharField(max_length=120)
    sub_text = models.TextField(default='/usr/local/bin/qsub')
    check_queue = models.CharField(max_length=180,
            default='/usr/local/maui/bin/showq')
    checked_time = models.DateTimeField(default=datetime.min)
    running = DictField()
    utilization = models.IntegerField(default=0)
    state = models.IntegerField(default=1)

    class Meta:
        app_label = 'qmpy'
        db_table = 'hosts'

    def __str__(self):
        return self.name

    @classmethod
    def interactive_create(cls):
        """
        Classmethod to create a Host model. Script will ask you questions about
        the host to add, and will return the created Host.

        """
        host = {}
        host['name'] = raw_input('Hostname:')
        if cls.objects.filter(name=host['name']).exists():
            print 'Host by that name already exists!'
            exit(-1)
        host['ip_address'] = raw_input('IP Address:')
        if cls.objects.filter(ip_address=host['ip_address']).exists():
            print 'Host at that address already exists!'
            exit(-1)
        host['ppn'] = raw_input('Processors per node:')
        host['nodes'] = raw_input('Max nodes to run on:')
        host['sub_script'] = raw_inputs('Command to submit a script '+
                '(e.g. /usr/local/bin/qsub):')
        host['check_queue'] = raw_input('Command for showq (e.g.'+
                '/usr/local/maui/bin/showq):')
        host['sub_text'] = raw_input('Path to qfile template:')
        h = cls(**host)
        h.save()

    @classmethod
    def get(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return cls(name=name)

    @property
    def accounts(self):
        return list(self.account_set.all())

    @property
    def jobs(self):
        jobs = []
        for acct in self.accounts:
            jobs += list(acct.job_set.filter(state=1))
        return jobs

    @property
    def active(self):
        if self.state < 1:
            return False
        elif self.utilization > self.nodes*self.ppn:
            return False
        else:
            return True

    @property
    def percent_utilization(self):
        return 100. * float(self.utilization) / (self.nodes*self.ppn)

    def get_utilization(self):
        util = 0
        for acct in self.account_set.all():
            for job in acct.job_set.filter(state=1):
                util += job.ncpus
        self.utilization = util
        return util

    def get_project(self):
        proj = Project.objects.filter(allocations__host=self, state=1)
        proj = proj.filter(task__state=0)
        if proj.exists():
            return random.choice(list(proj.distinct()))

    def get_tasks(self, project=None):
        tasks = queue.Task.objects.filter(state=0)
        if project is None:
            project = self.get_project()
            if project is None:
                return
        tasks = tasks.filter(project_set=project)
        tasks = tasks.filter(project_set__allocations__host=self)
        tasks = tasks.filter(project_set__users__account__host=self)
        return tasks.order_by('priority')

    @property
    def qfile(self):
        return open(self.sub_text).read()

    def get_binary(self, key):
        return self.binaries[key]

    def check_host(self):
        """Pings the host to see if it is online. Returns False if it is
        offline."""
        ret = subprocess.call("ping -c 1 -w 1 %s" % self.ip_address,
                shell=True,
                stdout=open('/dev/null', 'w'),
                stderr=subprocess.STDOUT)
        if ret == 0:
            return True
        else:
            self.state = -2
            self.save()
            return False

    @property
    def running_now(self):
        if datetime.now() + timedelta(seconds=-60) > self.checked_time:
            self.check_running()
        return self.running

    def check_running(self):
        """
        Uses the hosts data and one of the associated accounts to check the PBS
        queue on the Host. If it has been checked in the last 2 minutes, it
        will return the previously returned result.

        """
        self.checked_time = datetime.now()
        if self.state < 0:
            self.running = {}
            self.save()
            return
        account = random.choice(self.accounts)
        raw_data = account.execute(self.check_queue)
        running = {}
        if not raw_data:
            return
        for line in raw_data.split('\n'):
            if 'Active Jobs' in line:
                continue
            line = line.split()
            if len(line) != 9:
                continue
            try:
                running[int(line[0])] = {
                        'user':line[1],
                        'state':line[2],
                        'proc':int(line[3])}
            except:
                pass
        self.running = running
        self.save()
        
    def get_running(self):
        if self.running is not None:
            return self.running
        else:
            return {}

    @property
    def utilization_by_project(self):
        utilization = defaultdict(int)
        for job in self.jobs:
            projects = job.task.project_set.all()
            for p in projects:
                utilization[str(p.name)] += float(job.ncpus)/len(projects)
        if self.ppn*self.nodes > sum(utilization.values()):
            utilization["Idle"] = self.ppn*self.nodes - sum(utilization.values())
        return utilization

    @property
    def utilization_json(self):
        series = []
        for k, v in self.utilization_by_project.items():
            series.append({'data':v, 'label':k})
        return json.dumps(series)

    @property
    def ncpus(self):
        return self.ppn * self.nodes

#===============================================================================#

class Account(models.Model):
    """ 
    Base class for a `User` account on a `Host`. 

    Attributes:
        | host
        | id
        | job
        | run_path
        | state
        | user
        | username

    """

    user = models.ForeignKey(User)
    host = models.ForeignKey(Host)
    username = models.CharField(max_length=255)
    run_path = models.TextField()
    state = models.IntegerField(default=1)

    class Meta:
        app_label = 'qmpy'
        db_table = 'accounts'

    def __str__(self):
        return '{user}@{host}'.format(user=self.user.username, 
                host=self.host.name)

    @classmethod
    def get(cls, user, host):
        try:
            return Account.objects.get(user=user, host=host)
        except cls.DoesNotExist:
            return Account(host=host, user=user)

    @property
    def active(self):
        if self.state < 1:
            return False
        elif not self.host.active:
            return False
        else:
            return True

    def submit(self, path=None, run_path=None, qfile=None):
        self.execute('mkdir %s' % run_path, ignore_output=True)
        self.copy(folder=path, file='*', destination=run_path)
        cmd = 'cd {path} && {sub} {qfile}'.format(
                path=run_path, 
                sub=self.host.sub_script,
                qfile=qfile)
        stdout = self.execute(cmd)
        jid = int(stdout.split()[0].split('.')[0])
        return jid

    def execute(self, command='exit 0', ignore_output=False):
        ssh = 'ssh {user}@{host} "{cmd}"'.format(
                user=self.username,
                host=self.host.ip_address,
                cmd=command)

        logging.debug(ssh)

        call = subprocess.Popen(ssh, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        stdout,stderr = call.communicate()

        logging.debug('stdout: %s', stdout)
        logging.debug('stderr: %s', stderr)
        if stderr and not ignore_output:
            logging.warn('WARNING: %s', stderr)
        return stdout

    def copy(self, destination=None, to=None, # where to send the stuff
            fr=None, file=None, folder=None, # what to send
            clear_dest_dir=False, move=False): # some conditions on sending it

        if destination is None:
            destination = self.run_path
        if to is None:
            to = self
        if fr is None:
            if to == 'local':
                fr = self
            else:
                fr = 'local'

        assert (isinstance(to, Account) or to == 'local')
        assert (isinstance(fr, Account) or fr == 'local')
        assert ( not (file is None and folder is None) )

        send_dir = False
        if file is None:
            send_dir = True
        elif folder is None:
            folder = os.path.dirname(file)
            file = os.path.basename(file)
        
        if clear_dest_dir:
            if to == 'local':
                command = subprocess.Popen('rm -f %s/*' % destination,
                                                  stderr=subprocess.PIPE,
                                                  stdout=subprocess.PIPE)
                stdout, stderr = command.communicate()
            else:
                stdout, stderr = self.execute('rm -f %/*' % destination)
            logging.debug('stdout: %s', stdout)
            
        if fr == 'local':
            scp = 'scp '
        else:
            scp = 'scp {user}@{host}:'.format(
                    user=fr.username, host=fr.host.ip_address)

        if not file:
            scp += '-r '

        if send_dir:
            scp += os.path.abspath(folder)
        else:
            scp += '{path}/{file}'.format(
                    path=os.path.abspath(folder), file=file)

        if to == 'local':
            scp += ' '+destination
        else:
            scp += ' {user}@{host}:{path}'.format(
                user=to.username, host=to.host.ip_address, 
                path=os.path.abspath(destination))

        logging.debug('copy command: %s', scp)
        cmd = subprocess.Popen(scp,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        logging.debug('stdout: %s', stdout)
        logging.debug('stderr: %s', stderr)

        if move:
            if send_dir:
                rmcmd = 'rm -rf {path}'.format(path=os.path.abspath(folder))
            else:
                rmcmd = 'rm -f {path}/{file}'.format(file=file,
                        path=os.path.abspath(folder))
            logging.debug('wiping source: %s', rmcmd)
            stdout = fr.execute(rmcmd)
            logging.debug('output: %s', stdout)

#===============================================================================#

class Allocation(models.Model):
    """
    Base class for an Allocation on a computing resources.

    Attributes:
        | host
        | job
        | key
        | name
        | project
        | state
        | users

    """
    name = models.CharField(max_length=63, primary_key=True)
    key = models.CharField(max_length=100, default='')

    host = models.ForeignKey(Host)
    users = models.ManyToManyField(User)
    state = models.IntegerField(default=1)
    
    class Meta:
        app_label = 'qmpy'
        db_table = 'allocations'

    def __str__(self):
        return self.name
    
    @classmethod
    def create_interactive(cls):
        name = raw_input('Name your allocation:')
        if cls.objects.filter(name=name).exists():
            print 'Allocation by that name already exists!'
            exit(-1)
        host = raw_input('Which cluster is this allocation on?')
        if not Host.objects.filter(name=host).exists():
            print "This host doesn't exist!"
            exit(-1)
        host = Host.objects.get(name=host)
        alloc = cls(name=name, host=host)
        alloc.save()
        print 'Now we will assign users to this allocation'
        for acct in Account.objects.filter(host=host):
            inc = raw_input('Can %s use this allocation? y/n [y]:' % 
                    acct.user.name )
            if inc == 'y' or inc == '':
                alloc.users.add(acct.user)
        print 'If this allocation requires a special password, enter',
        key = raw_input('it now:')
        alloc.key=key
        alloc.save()

    @classmethod
    def get(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return cls(name=name)

    @property
    def active(self):
        if self.state < 1:
            return False
        elif not self.host.active:
            return False
        else:
            return True

    def get_user(self):
        return random.choice(self.users.filter(state=1))

    def get_account(self, users=None):
        if users is None:
            users = self.users.all()
        user = random.choice(list(users))
        return user.account_set.get(host=self.host)

    @property
    def percent_utilization(self):
        return self.host.percent_utilization

#===============================================================================#

class Project(models.Model):
    """
    Base class for a project within qmpy. 

    Attributes:
        | allocations
        | entry
        | name
        | priority
        | state
        | task
        | users

    """
    name = models.CharField(max_length=63, primary_key=True)
    priority = models.IntegerField(default=0)

    users = models.ManyToManyField(User)
    allocations = models.ManyToManyField(Allocation)
    state = models.IntegerField(default=1)
    class Meta:
        app_label = 'qmpy'
        db_table = 'projects'

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, name):
        if isinstance(name, cls):
            return name
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return cls(name=name)

    @property
    def completed(self):
        return self.task_set.filter(state=2)

    @property
    def running(self):
        return self.task_set.filter(state=1)

    @property
    def waiting(self):
        return self.task_set.filter(state=0).order_by('priority')

    @property
    def failed(self):
        return self.task_set.filter(state=-1)

    @classmethod
    def interactive_create(cls):
        name = raw_input('Name your project: ')
        if cls.objects.filter(name=name).exists():
            print 'Project by that name already exists!'
            exit(-1)
        proj = cls(name=name)
        proj.save()
        proj.priority = raw_input('Project priority (1-100): ')
        users = raw_input('List project users (e.g. sjk648 jsaal531 bwm291): ')
        for u in users.split():
            if not User.objects.filter(name=u).exists():
                print 'User named', u, 'doesn\'t exist!'
            else:
                proj.users.add(User.objects.get(name=u))

        alloc = raw_input('List project allocations (e.g. byrd victoria b1004): ')
        for a in alloc.split():
            if not Allocation.objects.filter(name=a).exists():
                print 'Allocation named', a, 'doesn\'t exist!'
            else:
                proj.allocations.add(Allocation.objects.get(name=a))

    @property
    def active(self):
        if self.state < 0:
            return False
        else:
            if self.state != 1:
                self.state = 1
                self.save()
            return True

    def get_allocation(self):
        available = [ a for a in self.allocations.all() if a.active ]
        if available:
            return random.choice(available)
        else:
            return []
