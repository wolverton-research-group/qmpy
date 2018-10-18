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

def sort_data(data, sorted_by=None, order='ascending'):
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
        if order == 'ascending':
            reverse = False
        elif order == 'descending':
            reverse = True
        return sorted(data, 
                      key=operator.itemgetter(sorted_by), 
                      reverse=reverse)
    except:
        return data

def search_data(request):
    """
    Input:
        request:
    Output:
        data: dict
            :form (django form format)
            :result (list of dictionaries)
            :count (int)
            :suburl (str)
    """
    data = {}
    if request.method == 'POST':
        form = DataFilterForm(request.POST)
        data['form'] = form

        if form.is_valid():
            kwargs = {}
            suburl_lst = []
            for arg in ['composition', 'calculated', 'band_gap',
                        'ntypes', 'generic']:
                tmp = form.cleaned_data.get(arg)
                if tmp != '':
                    kwargs[arg] = tmp
                    suburl_lst.append('%s=%s'%(arg, tmp))
            suburl = '&'.join(suburl_lst)

            with qmpy_rester.QMPYRester() as q:
                d = q.get_entries(verbose=False, **kwargs)
                sort_by = form.cleaned_data.get('sorted_by')
                order = form.cleaned_data.get('order')
                data['result'] = sort_data(d, sort_by, order)
                data['count'] = len(d)
                data['suburl'] = suburl
    else:
        form = DataFilterForm()
        data['form'] = form

    return render(request, 'api/search_data.html', data)
