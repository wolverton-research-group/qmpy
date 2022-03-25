from django.conf.urls import include, url

import django.views.generic
from django.views.generic import DetailView, ListView
from qmpy.db import settings

from rest_framework import routers
from qmpy.web import views
import os

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)


urlpatterns = [
    url(r"^$", views.home_page),
]

urlpatterns += [
    ## materials
    url(r"^materials/$", views.common_materials_view),
    url(r"^materials/structure/(?P<structure_id>.*)$", views.structure_view),
    url(r"^materials/composition/(?P<search>.*)$", views.composition_view),
    url(r"^materials/entry/(?P<entry_id>.*)$", views.entry_view),
    url(r"^materials/duplicates/(?P<entry_id>.*)$", views.duplicate_view),
    url(r"^materials/prototype/(?P<name>.*)$", views.prototype_view),
    url(r"^materials/prototypes$", views.prototypes_view),
    url(r"^materials/keyword/(?P<keyword>.*)$", views.keyword_view),
    url(
        r"^materials/generic_composition/(?P<search>.*)$",
        views.generic_composition_view,
    ),
    url(
        r"^materials/export/(?P<convention>.*)/(?P<format>.*)/(?P<structure_id>.*)",
        views.export_structure,
    ),
    url(
        r"^materials/export/(?P<format>.*)/(?P<structure_id>.*)", views.export_structure
    ),
    url(
        r"^materials/export/(?P<convention>.*)/(?P<structure_id>.*)",
        views.export_structure,
    ),
    url(r"^materials/export/(?P<structure_id>.*)", views.export_structure),
    url(r"^materials/xrd/(?P<structure_id>.*).csv", views.export_xrd),
    url(
        r"^materials/kpoints/(?P<mesh>.*)/(?P<structure_id>.*)/KPOINTS",
        views.export_kpoints,
    ),
    url(r"^materials/chem_pots", views.chem_pot_view),
    url(r"^materials/element_groups", views.element_group_view),
    url(r"^materials/deposit", views.deposit_view),
    ## References
    url(r"^reference/author/(?P<author_id>.*)$", views.author_view),
    url(r"^reference/journal/(?P<journal_id>.*)$", views.journal_view),
    url(r"^reference/(?P<reference_id>.*)$", views.reference_view),
    ## calculations
    url(r"^analysis/calculation/(?P<calculation_id>.*)$", views.calculation_view),
    ## analysis
    url(r"^analysis/$", views.analysis_view),
    url(r"^analysis/gclp/$", views.gclp_view),
    url(r"^analysis/phase_diagram/$", views.phase_diagram_view),
    url(r"^analysis/chemical_potentials/$", views.chem_pot_view),
    url(r"^analysis/spacegroup/(?P<spacegroup>.*)$", views.sg_view),
    url(r"^analysis/operation/(?P<operation>.*)$", views.op_view),
    url(r"^analysis/visualize$", views.vis_data),
    url(r"^analysis/visualize/custom$", views.jsmol),
    ## documentation
    url(r"^documentation/$", views.docs_view),
    url(r"^documentation/vasp$", views.vasp_docs),
    url(r"^documentation/structures$", views.structures_docs),
    url(r"^documentation/pots$", views.pots_docs),
    url(r"^documentation/overview$", views.overview_docs),
    url(r"^documentation/publications$", views.pubs_docs),
    ## api
    url(r"^api/$", views.api_view),
    url(r"^api/search", views.search_data),
    ## serializer
    url(r"^oqmdapi/entry$", views.EntryList.as_view()),
    url(r"^oqmdapi/entry/(?P<pk>[0-9]+)/$", views.EntryDetail.as_view()),
    url(r"^oqmdapi/calculation$", views.CalculationList.as_view()),
    url(r"^oqmdapi/calculation/(?P<pk>[0-9]+)/$", views.CalculationDetail.as_view()),
    url(r"^oqmdapi/formationenergy$", views.FormationEnergyList.as_view()),
    url(
        r"^oqmdapi/formationenergy/(?P<pk>[0-9]+)/$",
        views.FormationEnergyDetail.as_view(),
    ),
    ## optimade
    url(r"^optimade/$", views.optimade_view),
    url(r"^optimade/info$", views.OptimadeInfoData),
    url(r"^optimade/versions$", views.OptimadeVersionsData),
    url(r"^optimade/structures$", views.OptimadeStructureList.as_view()),
    url(
        r"^optimade/structures/(?P<pk>[0-9]+)/$",
        views.OptimadeStructureDetail.as_view(),
    ),
    url(r"^optimade/info/structures$", views.OptimadeStructuresInfoData),
    url(r"^optimade/links$", views.OptimadeLinksData),
    url(r"^optimade/v1/info$", views.OptimadeInfoData),
    url(r"^optimade/versions$", views.OptimadeVersionsData),
    url(r"^optimade/v1/structures$", views.OptimadeStructureList.as_view()),
    url(
        r"^optimade/v1/structures/(?P<pk>[0-9]+)/$",
        views.OptimadeStructureDetail.as_view(),
    ),
    url(r"^optimade/v1/info/structures$", views.OptimadeStructuresInfoData),
    url(r"^optimade/v1/links$", views.OptimadeLinksData),
    url(r"^optimade/v\d+$", views.OptimadeVersionPage),
    ## download
    url(r"^download/", views.download_home),
    ## other
    url(r"^faq", views.faq_view),
]

if os.environ.get("OQMD_WEB_debug").lower() == "true":
    urlpatterns += [
        url(r"^materials/discovery", views.disco_view),
        ## computing
        url(r"^computing/$", views.computing_view),
        url(r"^computing/projects$", views.projects_view),
        url(r"^computing/hosts$", views.hosts_view),
        url(r"^computing/queue$", views.queue_view),
        url(r"^computing/onlinesubmit$", views.online_view),
        url(r"^computing/create/host$", views.new_host_view),
        # url(r'^computing/create/project', views.new_project_view),
        # url(r'^computing/create/user',    views.new_user_view),
        # url(r'^computing/create/',        views.new_user_view),
        url(
            r"^computing/project/(?P<state>.*)/(?P<project_id>.*)$",
            views.project_state_view,
        ),
        url(r"^computing/project/(?P<project_id>.*)$", views.project_view),
        url(r"^computing/host/(?P<host_id>.*)$", views.host_view),
        url(r"^computing/user/(?P<user_id>.*)$", views.user_view),
        url(r"^computing/allocation/(?P<allocation_id>.*)$", views.allocation_view),
        url(r"^computing/task/(?P<task_id>.*)$", views.task_view),
        url(r"^computing/job/(?P<job_id>.*)$", views.job_view),
        # other
        url(r"^playground", views.play_view),
    ]
else:
    urlpatterns += [
        url(r"^robots.txt", views.robots_view),
    ]
