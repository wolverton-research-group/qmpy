from qmpy import *
import os, os.path

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

groups = [
        {
            'W': ['W','Mo','Cr','Te','Se'], 
            'Nd':['La', 'Bi', 'Ce','Nd','Sm','Gd','Y','Yb','In','Sb',
                  'Sc','Nb','Ta','Mo','Ti','Fe','V','Ga','Cr']},
        {
            'Nd': ['Te','Ce','Pb','Zr','Hf'], 
            'W':['Nb','Ta','W','Mo','V','Cr']},
        {
            'Nd': ['Bi','Nb','Ta','W','Mo'], 
            'W':['Al','In','Ga','Y','Sc','Ti','V','Cr','Fe','Mn','Co','Cu']},
        ]

mkdir('../quaternaries/')
mkdir('../quaternaries/garnet')
mkdir('../quaternaries/garnet/O')
a = 'Li'

s = io.poscar.read('quaternaries/garnet-Li3Nd3W2O12')
for group in groups:
    for b,c in sorted(itertools.product(group['Nd'], group['W'])):
        print "Li3{b}3{c}2O12".format(b=b, c=c)
        path = '../quaternaries/garnet/O/{a}_{b}_{c}'.format(a=a,b=b,c=c)
        name = '{a}_{b}_{c}'.format(a=a,b=b,c=c)
        mkdir(path)
        new = s.substitute({'Nd':b, 'W':c})

        io.poscar.write(new, path+'/POSCAR')
        if Entry.objects.filter(path=os.path.abspath(path)).exists():
            continue

        entry = Entry.create(path+'/POSCAR',
                             projects=['garnets'],
                             keywords=['garnet', 'quaternary'])
        entry.save()
        task = Task.create(entry, 'static')
        task.save()
        print entry

