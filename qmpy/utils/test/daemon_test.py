from qmpy.utils import Daemon
import time
import os.path

p = os.path.dirname(os.path.abspath(__file__))
print p

class TaskManager(Daemon):
    def run(self):
        open(p+'/tasks.txt','w').write('\n'.join([ 'task-%d' % i for i in range(10)]))
        while True:
            tasks = open(p+'/tasks.txt').readlines()
            if tasks:
                task = tasks.pop(0).strip()
                print 'running task:', task
                open(p+'/jobs.txt','a').write('job-%s\n' %
                        task.replace('task-', ''))
            open(p+'/tasks.txt','w').write(''.join(tasks))
            time.sleep(1)

def JobManager(Daemon):
    def run(self):
        while True:
            jobs = open(p+'/jobs.txt').readlines()
            if jobs:
                job = jobs.pop(0)
                print 'finished %s' % (job.replace('job-', ''))
            open(p+'/jobs.txt','w').write(''.join(jobs))
            time.sleep(1)

tm = TaskManager(p+'/tm.pid', stdout='/dev/stdout', stderr='/dev/stderr')
jm = JobManager(p+'/jm.pid')

tm.start()
jm.start()
