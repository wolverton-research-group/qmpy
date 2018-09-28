import json
import os.path
import time
import sys
import logging
import logging.handlers
from datetime import datetime, timedelta

import django.db as ddb
from django.db import transaction

import qmpy
import queue
import resources as rsc
import qmpy.utils.daemon as daemon
import qmpy.analysis.vasp.calculation as vasp

logger = logging.getLogger(__name__)

jlogger = logging.getLogger('JobManager')
tlogger = logging.getLogger('TaskManager')

jfile = os.path.join(qmpy.LOG_PATH, 'job_manager.log')
tfile = os.path.join(qmpy.LOG_PATH, 'task_manager.log')

jlog_file = logging.handlers.WatchedFileHandler(jfile)
tlog_file = logging.handlers.WatchedFileHandler(tfile)

jlog_file.setFormatter(qmpy.formatter)
tlog_file.setFormatter(qmpy.formatter)

jlogger.addHandler(jlog_file)
tlogger.addHandler(tlog_file)

jlogger.setLevel(logging.INFO)
tlogger.setLevel(logging.INFO)

def check_die(n=None):
    if n is None:
        if os.path.exists('/home/oqmd/controls/stop/running'):
            sys.exit(0)
    else:
        for i in range(n):
            time.sleep(1)
            check_die()

class JobManager(daemon.Daemon):
    """
    Class to manage collection of running Job objects. When running, it
    collects any Job whose is_done method evaluates to True. While the manager
    is running (as a Daemon or normally) it will look for a file named "die" in
    the home directory of the user who initialized the manager, and if found it
    will stop cleanly.

    """
    def run(self):
        os.umask(022)
        while True:
            ddb.reset_queries()
            jobs = queue.Job.objects.filter(state=1, account__host__state=1,
                    created__lt=datetime.now() - timedelta(seconds=-200000000))
            for job in jobs:
                check_die()
                if job.is_done():
                    jlogger.info('Collected %s' % job)
                    job.collect()
            check_die(20)

class TaskManager(daemon.Daemon):
    """
    Class to manage creation of Job objects from uncompleted Tasks. While
    running it finds the next available Task (based on additional keyword
    arguments) and attempts to submit all Jobs return by the tasks get_jobs()
    method. While the manager is running (as a Daemon or normally) it will 
    look for a file named "die" in the home directory of the user who 
    initialized the manager, and if found it will stop cleanly.

    Conditions for Task eligibility are:
        - A resource assosiated with the Task (via its projects list) has CPUs
          available.
        - if the manager is called with the project keyword, only Tasks
          associated with that project will be run
        - if the manager is called with the path keyword, only Tasks whose
          entry contain the path or path fragment will be run.
    """
    def run(self, project=None):
        os.umask(022)
        while True:
            check_die()
            ddb.reset_queries()
            for host in rsc.Host.objects.filter(state=1):
                self.fill_host(host, project=project)
            check_die(60)

    def fill_host(self, host, project=None):
        host.get_utilization()
        host.save()
        tlogger.debug('starting host %s', host.name)
        while True:
            check_die()
            if host.utilization >= 1.5*host.nodes*host.ppn:
                tlogger.debug('Host utilization reached 100%')
                return
            tasks = host.get_tasks(project=project)
            if not tasks:
                tlogger.debug('No tasks remaining')
                return 
            task = tasks[0]
            self.handle_task(task, host)

    def handle_task(self, task, host):
        os.umask(022)
        t0 = time.time()
        tlogger.info('Processing: Task %s (Entry %s)' % 
                (task.id, task.entry.id))
        try:
            jobs = task.get_jobs(host=host)
        except queue.ResourceUnavailableError:
            raise
        except vasp.VaspError, err:
            task.fail()
            task.save()
            tlogger.warn('VASP error: %s', err)
            return
        except Exception, err:
            task.hold()
            task.save()
            tlogger.warn('Unknown error processing task: %s' % err)
            return

        if not jobs:
            task.complete()
            tlogger.info('Finished: Task %s (Entry %s)' %
                    (task.id, task.entry.id))

        for job in jobs:
            nattempts = 1
            while not job.state == 1:
                if nattempts == 2:
                    break
                check_die()
                try:
                    job.submit()
                    if job.account.host == 'quest':
                        time.sleep(50)
                except Exception:
                    tlogger.warn('Submission error, waiting 30 seconds'
                            ' (Host %s), Task: %s, Entry: %s' % (host.name,
                                task.id, task.entry.id))
                    check_die(60)
                    nattempts += 1
            job.save()
            host.utilization += job.ncpus
            tlogger.info('Submitted: %s (Entry %s)' % (task.id, task.entry.id))

        task.save()
        with transaction.atomic():
            try:
                task.entry.save()
            except Exception, err:
                task.hold()
                task.save()
                tlogger.warn('Unknown error processing task: %s' % err)

