import os.path

from django.contrib.auth import authenticate
from django.shortcuts import render_to_response
from django.template import RequestContext
from qmpy.models import Entry, Task, Calculation, Formation, MetaData
from tools import get_globals

def home_page(request):
    data = get_globals()
    data.update({
        'done':Entry.objects.filter(
            formationenergy__fit='standard').distinct(),
        'running':Task.objects.filter(state=1),
        'recent':Calculation.objects.filter(label='static',
            converged=True).order_by('-id')[:5]})
    request.session.set_test_cookie()
    return render_to_response('index.html',
            data,
            RequestContext(request))

def construction_page(request):
    return render_to_response('construction.html',
            {},
            RequestContext(request))

def faq_view(request):
    return render_to_response('faq.html')

def play_view(request):
    return render_to_response('play.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                pass
        else:
            pass

def logout(request):
    logout(request)
    # redirect to success
