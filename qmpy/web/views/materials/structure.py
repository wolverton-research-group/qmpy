from tempfile import mkstemp
import os.path
import csv
import cStringIO


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *
from qmpy.io import write
from ..tools import get_globals

def structure_view(request, structure_id):
    structure = Structure.objects.get(pk=structure_id)
    data = get_globals()

    if request.method == "POST":
        p = request.POST
        data['primitive'] = bool(int(p['primitive']))
        if data['primitive']:
            structure.make_primitive()
        else:
            structure.make_conventional()

    atoms = [ {'element': a.element_id, 'x': a.x, 'y':a.y, 'z':a.z} 
            for a in structure ]

    lp = structure.lat_param_dict
    if abs(lp['a'] - lp['b']) < 1e-4:
        if abs(lp['a'] - lp['c']) < 1e-4:
            lpstr = 'a = b = c = %3f' % lp['a']
        else:
            lpstr = 'a = b = %3f, c = %3f' % ( lp['a'], lp['c'])
    else:
        lpstr = 'a = %3f, b = %3f, c = %3f' % (lp['a'], lp['b'], lp['c'])

    lpstr += '<br>'

    if abs(lp['alpha'] - lp['beta']) < 1e-2:
        if abs(lp['alpha'] - lp['gamma']) < 1e-2:
            lpstr += '&alpha; = &beta; = &gamma; = %3f' % lp['alpha']
        else:
            lpstr += '&alpha; = &beta; = %3f, &gamma; = %3f' % ( 
                     lp['alpha'], lp['gamma'])
    else:
        lpstr += '&alpha; = %3f, &beta; = %3f, &gamma; = %3f' % (
                 lp['alpha'], lp['beta'], lp['gamma'])

    pdf = structure.get_pdf()
    xrd = structure.get_xrd()

    data['structure'] = structure
    data['lpstr'] = lpstr
    data['pdf'] = pdf.plot().get_flot_script(div='pdf')
    data['xrd'] = xrd.plot().get_flot_script(div='xrd')
    data.update(csrf(request))
    return render_to_response('materials/structure.html', 
            data,
            RequestContext(request))

def export_structure(request, structure_id, convention='primitive', format='poscar'):
    s = Structure.objects.get(id=structure_id)
    structstr = write(s, format=format, convention=convention, wrap=True)
    fileobj = cStringIO.StringIO(structstr)
    return HttpResponse(fileobj.getvalue(), 'text/plain')

def prototype_view(request, name):
    proto = Prototype.objects.get(pk=name)
    n_stable = 0
    for entry in proto.entry_set.all():
        if entry.stable:
            n_stable += 1
    data = get_globals()
    data['prototype'] = proto
    data['n_stable'] = n_stable
    if request.method == 'POST':
        data['primitive'] = request.POST.get('primitive')

    structure = proto.structure
    if not structure:
        example = proto.entry_set.all()
        if example.exists():
            structure = example[0].structure
    data['structure'] = structure

    data.update(csrf(request))
    return render_to_response('materials/prototype.html', 
            data,
            RequestContext(request))

def prototypes_view(request):
    data = get_globals()
    return render_to_response('materials/prototypes.html',
            data,
            RequestContext(request))

def export_xrd(request, structure_id):
    s = Structure.objects.get(pk=structure_id)
    xrd = s.get_xrd()
    data = '\n'.join([','.join(map(str,
        [p.two_theta, p.intensity, p.multiplicity, p.hkl[0]])) for p in
        xrd.peaks])
    f = cStringIO.StringIO(data)
    return HttpResponse(f.getvalue(), 'text/csv')

def export_kpoints(request, structure_id, mesh=8000):
    s = Structure.objects.get(pk=structure_id)
    c = Calculation()
    c.settings = {'kppra':float(mesh), 'gamma':True}
    c.input = s
    f = cStringIO.StringIO(c.get_kpoints())
    return HttpResponse(f.getvalue(), 'text/plain')
