from django.contrib.auth import authenticate
from django.shortcuts import render
from qmpy.models import Entry, Task, Calculation, Formation, MetaData
from .tools import get_globals
from django.http import HttpResponse


def home_page(request):
    data = get_globals()
    data.update(
        {
            "done": "{:,}".format(Formation.objects.filter(fit="standard").count()),
        }
    )
    request.session.set_test_cookie()
    return render(request, "index.html", data)


def construction_page(request):
    return render(request, "construction.html", {})


def faq_view(request):
    return render(request, "faq.html")


def play_view(request):
    return render(request, "play.html")


def robots_view(request):
    lines = [
        "User-agent: Googlebot",
        "User-agent: Bingbot",
        "User-agent: DuckDuckBot",
        "Disallow: /optimade/structures*",
        "Disallow: /oqmdapi/*",
        "Disallow: /api/search*",
        "Disallow: /materials/export*",
        "Disallow: /analysis/visualize/custom*",
        "\n",
        "User-agent: *",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
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
