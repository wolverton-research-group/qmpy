from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from search_data_forms import DataFilterForm
from qmpy.rester import qmpy_rester

import logging
logger = logging.getLogger(__name__)

def search_data(request):
    data = {}
    if request.method == 'POST':
        form = DataFilterForm(request.POST)
        data['form'] = form

        if form.is_valid():
            kwargs = {}
            for arg in ['composition', 'calculated', 'band_gap',
                        'ntypes', 'generic']:
                kwargs[arg] = form.cleaned_data.get(arg)

            with qmpy_rester.QMPYRester() as q:
                data['result'] = q.get_entries(verbose=False, **kwargs)
    else:
        form = DataFilterForm()
        data['form'] = form

    return render(request, 'api/search_data.html', data)
