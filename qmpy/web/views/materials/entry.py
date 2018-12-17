from tempfile import mkstemp
import os.path

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *
from ..tools import get_globals
import glob

def entry_view(request, entry_id):
    entry = Entry.objects.get(pk=entry_id)
    data = {'entry': entry}
    data = get_globals(data)
    if request.method == 'POST':
        p = request.POST

        data['primitive'] = bool(int(p.get('primitive', '0')))
        if p.get('calculate'):
            t = Task.create(entry, 'static')
            t.save()

        if p.get('req_pbe'):
            pass

        if p.get('req_hse'):
            pass

        if p.get('recollect_calc'):
            entry.calculation_set.all().delete()
            entry.structure_set.all().delete()
            entry.task_set.all().delete()
            entry.job_set.all().delete()

            outcars = glob.glob(os.path.join(entry.path, '*', 'OUTCAR.gz'))
            for outcar in outcars:
                calc_path = os.path.dirname(outcar)
                try:
                    calc = Calculation.read(calc_path)
                except Exception,e:
                    print outcar,' has error:'
                    print e
                    raise
                    continue
                calc.set_label(os.path.basename(calc_path))
                calc.input.set_label(calc.label + '_input')
                try:
                    calc.output.set_label(calc.label + '_output')
                except Exception,e:
                    print outcar,' has error:'
                    print e
                    continue
                calc.configuration = os.path.basename(calc_path)
                try:
                    calc.read_outcar()
                except Exception,e:
                    print outcar,' has error:'
                    print e
                    continue
                calc.read_stdout()
                if calc.converged:
                    calc.read_doscar()
                    try:
                        calc.get_band_gap_from_occ()
                    except:
                        pass
                else:
                    print calc.id, calc_path, "NOT CONVERGED"
                calc.entry = entry
                calc.save()
            entry.structure.symmetrize()
            entry.save()


        if p.get('add_keyword'):
            kw = MetaData.get('Keyword', p['add_keyword'])
            kw.entry_set.add(entry)
        if p.get('add_hold'):
            hold = MetaData.get('Hold', p['add_hold'])
            hold.entry_set.add(entry)

    #pdf = get_pdf(entry.input)
    #data['pdf'] = pdf.get_flot_script()

    data.update(csrf(request))
    return render_to_response('materials/entry.html', 
            data, 
            RequestContext(request))


def keyword_view(request, keyword):
    key = MetaData.get('Keyword', keyword)

    data = get_globals()
    data['keyword'] = key
    return render_to_response('materials/keyword.html', 
            data, 
            RequestContext(request))

def duplicate_view(request, entry_id):
    entries = Entry.objects.filter(duplicate_of=entry_id)
    data = get_globals()
    data['entries'] = entries
    data['entry'] = Entry.objects.get(pk=entry_id)
    return render_to_response('materials/duplicates.html',
            data,
            RequestContext(request))
