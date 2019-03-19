from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from django.core.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.apis import APIKey
from api_forms import APIKeyForm

import logging
logger = logging.getLogger(__name__)

def api_key_gen(request):
    data = {}
    if request.method == 'POST':
        form = APIKeyForm(request.POST)
        data['form'] = form
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            apiuser = APIKey.create(username=username, email=email)
            data['key'] = apiuser.key
    else:
        form = APIKeyForm()
        data['form'] = form


    return render(request, 'api/api_gen.html', data)
