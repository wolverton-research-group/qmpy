from django.http import HttpResponse, QueryDict
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
        p = request.POST
        if 'next' in p:
            request_post = p.get('next')
            rp = QueryDict(request_post, mutable=True)
            nextoffset = int(rp.get('sort_offset')) + int(rp.get('limit'))
            rp.update({'sort_offset': nextoffset})
            form = DataFilterForm(rp)
            data['request_post'] = rp.urlencode()
        elif 'prev' in p:
            request_post = p.get('prev')
            rp = QueryDict(request_post, mutable=True)
            prevoffset = max(0, 
                             int(rp.get('sort_offset')) - \
                             int(rp.get('limit'))
                            )
            rp.update({'sort_offset': prevoffset})
            form = DataFilterForm(rp)
            data['request_post'] = rp.urlencode()
        elif 'front' in p:
            request_post = p.get('front')
            rp = QueryDict(request_post, mutable=True)
            rp.update({'sort_offset': 0})
            form = DataFilterForm(rp)
            data['request_post'] = rp.urlencode()
        elif 'end' in p:
            request_post = p.get('end')
            rp = QueryDict(request_post, mutable=True)
            endoffset = int(rp.get('count')) - int(rp.get('limit'))
            rp.update({'sort_offset': endoffset})
            form = DataFilterForm(rp)
            data['request_post'] = rp.urlencode()
        elif 'clear' in p:
            form = DataFilterForm()
        else:
            form = DataFilterForm(p)
            data['request_post'] = p.urlencode()
        data['form'] = form

        if form.is_valid():
            kwargs = {} # input kwargs for QMPYRester()

            ## Collect information from django forms 
            # General paramters
            # These parameters are from django forms. Only 'sort_offest'
            # can be passed from django forms and 'offset' cannot be 
            # initialiated from django forms.
            for arg in ['composition', 'icsd', 'filter', 'noduplicate',
                        'element_set', 'prototype', 'generic',
                        'volume', 'natoms', 'ntypes', 'stability',
                        'delta_e', 'band_gap',
                        'sort_by', 'desc', 'sort_offset', 'limit']:
                tmp = form.cleaned_data.get(arg)
                if tmp != '' and tmp != None:
                    if arg == 'element_set':
                        tmp = tmp.replace(' ','')
                        tmp = tmp.replace('%20','')
                    kwargs[arg] = tmp

            # Update 'offset'
            # The django form will store the value of 'offset' input
            # as 'sort_offset'. If sorting is not needed, this value
            # should be the offset of total result. 
            if 'sort_by' not in kwargs and 'sort_offset' in kwargs:
                kwargs['offset'] = kwargs['sort_offset']

            # Include necessary info
            output_fields_list = ['name', 'entry_id', 'icsd_id', 'composition_generic',
                                 'spacegroup', 'prototype', 'ntypes', 'natoms',
                                 'volume', 'delta_e', 'band_gap', 'stability']
            kwargs['fields'] = ','.join(output_fields_list)

            # Call QMPYRester() to collect data
            with qmpy_rester.QMPYRester() as q:
                d = q.get_oqmd_phases(verbose=False, **kwargs)
                data['suburl'] = q.suburl
                data['result'] = d['data'] #['results']
                data['limit'] = kwargs.get('limit', 50) # default of limit is 50
                data['offset'] = kwargs.get('sort_offset', 0) 
                data['sort_by'] = kwargs.get('sort_by', None) 

                if 'sort_by' in kwargs:
                    kwargs.pop('sort_by', None)
                    kwargs['limit'] = 1 # To get the count of total result, we
                                        # need another url request. But this time
                                        # we only need to output one entry per page.
                    kwargs['offset'] = 0
                    data['count'] = q.get_oqmd_phases(verbose=False, **kwargs)['meta']['data_available']
                else:
                    data['count'] =  d['meta']['data_available']

                if data['offset'] > 0:
                    data['prev'] = True
                if data['offset'] + data['limit'] < data['count']:
                    data['next'] = True

                if data['offset'] < 0:
                    data['offset'] = 0

                data['start'] = data['offset'] + 1
                data['end'] = min(data['count'], 
                                  data['offset'] + data['limit'])

                if 'count=' not in data['request_post']:
                    data['request_post'] += '&count=' +\
                                             str(data['count'])
    else:
        form = DataFilterForm()
        data['form'] = form

    return render(request, 'api/search_data.html', data)
