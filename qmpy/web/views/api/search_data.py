from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from search_data_forms import DataFilterForm
from qmpy.rester import qmpy_rester

import operator

import logging
logger = logging.getLogger(__name__)

def sort_data(data, sorted_by=None):
    """
    Input:
        data: list of dictionaries
        sorted_by: str
    Output:
        list of dictionaries
    """
    if not sorted_by:
        return data
    try:
        return sorted(data, key=operator.itemgetter(sorted_by))
    except:
        return data

def search_data(request):
    data = {}
    if request.method == 'POST':
        form = DataFilterForm(request.POST)
        data['form'] = form

        if form.is_valid():
            kwargs = {}
            for arg in ['composition', 'calculated', 'band_gap',
                        'ntypes', 'generic']:
                tmp = form.cleaned_data.get(arg)
                if tmp != '':
                    kwargs[arg] = tmp

            with qmpy_rester.QMPYRester() as q:
                d = q.get_entries(verbose=False, **kwargs)
                sort_by = form.cleaned_data.get('sorted_by')
                data['result'] = sort_data(d, sort_by)
    else:
        form = DataFilterForm()
        data['form'] = form

    return render(request, 'api/search_data.html', data)
