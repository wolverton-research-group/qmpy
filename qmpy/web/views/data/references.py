import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pylab as plt
import StringIO

from django.shortcuts import render_to_response
from django.template import RequestContext

from ..tools import get_globals
from qmpy.models import Author, Journal, Reference, Entry
from qmpy.utils import *

def reference_view(request, reference_id):
    ref = Reference.objects.get(id=reference_id)
    data = get_globals()
    data['reference'] = ref
    return render_to_response('data/reference/paper.html', 
            data,
            RequestContext(request))

def journal_view(request, journal_id):
    journal = Journal.objects.get(id=journal_id)
    dates = journal.references.values_list('year', flat=True)
    plt.hist(dates)
    plt.xlabel('Year')
    plt.ylabel('# of publications with new materials')
    img = StringIO.StringIO()
    plt.savefig(img, dpi=75, bbox_inches='tight')
    data_uri = 'data:image/jpg;base64,'
    data_uri += img.getvalue().encode('base64').replace('\n', '')
    plt.close()

    some_entries = Entry.objects.filter(reference__journal=journal)[:20]
    data = get_globals()
    data.update({'journal':journal, 
        'hist':data_uri,
        'entries':some_entries})
    return render_to_response('data/reference/journal.html', 
            data,
            RequestContext(request))


def author_view(request, author_id):
    author = Author.objects.get(id=author_id)
    materials = Entry.objects.filter(reference__author_set=author)
    coauths = {}
    for co in Author.objects.filter(references__author_set=author):
        papers = Reference.objects.filter(author_set=author)
        papers = papers.filter(author_set=co)
        mats = Entry.objects.filter(reference__in=papers)
        data = {'papers': papers.distinct().count(),
                'materials': mats.distinct().count()}
        coauths[co] = data

    data = get_globals()
    data.update({'author':author,
        'materials':materials,
        'coauthors':coauths})
    return render_to_response('data/reference/author.html', 
            data,
            RequestContext(request))

