from qmpy import *
import django.db as ddb

i = 0
for c in Calculation.objects.filter(converged=True, label__in=['static',
            'standard'], formationenergy=None):
    f = c.compute_formation()
    f.save()
    print f
    i += 1
    if i % 1000 == 0:
        ddb.reset_queries()
