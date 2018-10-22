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
                        'ntypes', 'generic',
                        'sort_by', 'desc',
                        'sort_limit', 'sort_offset']:
                tmp = form.cleaned_data.get(arg)
                if tmp != '' and tmp != None:
                    kwargs[arg] = tmp
                    suburl_lst.append('%s=%s'%(arg, tmp))
            suburl = '&'.join(suburl_lst)
            data['suburl'] = suburl

            with qmpy_rester.QMPYRester() as q:
                d = q.get_entries(verbose=False, **kwargs)
                data['result'] = d['results']
                
                if 'sort_by' in kwargs:
                    kwargs.pop('sort_by', None)
                    kwargs['limit'] = 1
                    kwargs['offset'] = 0
                    data['count'] = q.get_entries(verbose=False, **kwargs)['count']
                else:
                    data['count'] = d['count']
    else:
        form = DataFilterForm()
        data['form'] = form

    return render(request, 'api/search_data.html', data)
