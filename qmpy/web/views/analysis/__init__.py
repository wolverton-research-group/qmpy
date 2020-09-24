from django.shortcuts import render

from .symmetry import *
from .visualize import *
from .thermodynamics import *
from .calculation import *


def analysis_view(request):
    return render(request, "analysis/index.html", {})
