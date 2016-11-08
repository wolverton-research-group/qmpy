from tempfile import mkstemp
import os.path

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *
from ..tools import get_globals

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

