from tempfile import mkstemp
import os.path

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.context_processors import csrf

from qmpy import INSTALL_PATH
from qmpy.models import *
from ..tools import get_globals


def entry_view(request, entry_id):
    entry = Entry.objects.get(pk=entry_id)
    data = {"entry": entry}

    if entry.calculation_set.filter(label="static").count() != 0:
        data["entry_structure"] = entry.calculation_set.filter(label="static")[0].output
    elif entry.calculation_set.filter(label="standard").count() != 0:
        data["entry_structure"] = entry.calculation_set.filter(label="standard")[
            0
        ].output
    else:
        data["entry_structure"] = entry.input

    fe_std = entry.formationenergy_set.filter(fit='standard')
    data['structured_data'] = {}
    if fe_std:
        data['structured_data']['available'] = True
        data['structured_data']["name"]       = "{} {}".format(entry.spacegroup.lattice_system, entry.name)
        data['structured_data']["is_stable"]  = True if fe_std[0].stability <= 0.0 else False
        data['structured_data']["stability"]  = max(fe_std[0].stability,0.0)
        data['structured_data']["spacegroup"] = "{} ({})".format(entry.spacegroup.hm, entry.spacegroup.number)
        data['structured_data']["volume"]     = fe_std[0].calculation.output.volume
        data['structured_data']["bandgap"]    = fe_std[0].calculation.band_gap
        data['structured_data']["natoms"]     = fe_std[0].entry.natoms
        data['structured_data']["delta_e"]    = fe_std[0].delta_e
        data['structured_data']["handle"]     = "http://hdl.handle.net/20.500.12856/oqmd.v1.ent.{}".format(entry.id)
        if "icsd" in entry.path:
            data['structured_data']["icsd"]   = "This structure was obtained from ICSD (Collection code = {})".format(entry.path.split('/')[-1])
        else:
            data['structured_data']["icsd"]   = ""
        
    data = get_globals(data)
    if request.method == "POST":
        p = request.POST

        data["primitive"] = bool(int(p.get("primitive", "0")))
        if p.get("calculate"):
            t = Task.create(entry, "static")
            t.save()

        if p.get("add_keyword"):
            kw = MetaData.get("Keyword", p["add_keyword"])
            kw.entry_set.add(entry)
        if p.get("add_hold"):
            hold = MetaData.get("Hold", p["add_hold"])
            hold.entry_set.add(entry)

    # pdf = get_pdf(entry.input)
    # data['pdf'] = pdf.get_flot_script()

    data.update(csrf(request))
    return render_to_response("materials/entry.html", data, RequestContext(request))


def keyword_view(request, keyword):
    key = MetaData.get("Keyword", keyword)

    data = get_globals()
    data["keyword"] = key
    return render_to_response("materials/keyword.html", data, RequestContext(request))


def duplicate_view(request, entry_id):
    entries = Entry.objects.filter(duplicate_of=entry_id)
    data = get_globals()
    data["entries"] = entries
    data["entry"] = Entry.objects.get(pk=entry_id)
    return render_to_response(
        "materials/duplicates.html", data, RequestContext(request)
    )
