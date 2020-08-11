from django.conf.urls import patterns, include, url

import django.views.generic
from django.views.generic import DetailView, ListView
from django.contrib import admin
from qmpy.db import settings

from rest_framework import routers
from qmpy.web import views

#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = [
    url(r'^$', 'qmpy.web.views.home_page'),

    ## admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/login/.*$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/.*$', 'django.contrib.auth.views.logout'),
    url(r'^admin/', include(admin.site.urls)),

    ]

urlpatterns += [
    ## materials
    url(r'^materials/$', 'qmpy.web.views.common_materials_view'),
    url(r'^materials/structure/(?P<structure_id>.*)$', 'qmpy.web.views.structure_view'),
    url(r'^materials/composition/(?P<search>.*)$', 'qmpy.web.views.composition_view'),
    url(r'^materials/entry/(?P<entry_id>.*)$', 'qmpy.web.views.entry_view'),
    url(r'^materials/duplicates/(?P<entry_id>.*)$', 'qmpy.web.views.duplicate_view'),
    url(r'^materials/prototype/(?P<name>.*)$', 'qmpy.web.views.prototype_view'),
    url(r'^materials/prototypes$', 'qmpy.web.views.prototypes_view'),
    url(r'^materials/keyword/(?P<keyword>.*)$', 'qmpy.web.views.keyword_view'),
    url(r'^materials/generic_composition/(?P<search>.*)$', 'qmpy.web.views.generic_composition_view'),

    url(r'^materials/export/(?P<convention>.*)/(?P<format>.*)/(?P<structure_id>.*)',
        'qmpy.web.views.export_structure'),
    url(r'^materials/export/(?P<format>.*)/(?P<structure_id>.*)', 'qmpy.web.views.export_structure'),
    url(r'^materials/export/(?P<convention>.*)/(?P<structure_id>.*)', 'qmpy.web.views.export_structure'),
    url(r'^materials/export/(?P<structure_id>.*)', 'qmpy.web.views.export_structure'),
    url(r'^materials/xrd/(?P<structure_id>.*).csv', 'qmpy.web.views.export_xrd'),
    url(r'^materials/kpoints/(?P<mesh>.*)/(?P<structure_id>.*)/KPOINTS',
        'qmpy.web.views.export_kpoints'),
    url(r'^materials/discovery', 'qmpy.web.views.disco_view'),
    url(r'^materials/chem_pots', 'qmpy.web.views.chem_pot_view'),
    url(r'^materials/element_groups', 'qmpy.web.views.element_group_view'),
    url(r'^materials/deposit', 'qmpy.web.views.deposit_view'),

    ## References
    url(r'^reference/author/(?P<author_id>.*)$', 'qmpy.web.views.author_view'),
    url(r'^reference/journal/(?P<journal_id>.*)$', 'qmpy.web.views.journal_view'),
    url(r'^reference/(?P<reference_id>.*)$', 'qmpy.web.views.reference_view'),

    ## calculations
    url(r'^analysis/calculation/(?P<calculation_id>.*)$', 'qmpy.web.views.calculation_view'),

    ## computing
    url(r'^computing/$', 'qmpy.web.views.computing_view'),
    url(r'^computing/projects$', 'qmpy.web.views.projects_view'),
    url(r'^computing/hosts$', 'qmpy.web.views.hosts_view'),
    url(r'^computing/queue$', 'qmpy.web.views.queue_view'),
    url(r'^computing/onlinesubmit$', 'qmpy.web.views.online_view'),

    url(r'^computing/create/host$', 'qmpy.web.views.new_host_view'),
    #url(r'^computing/create/project', 'qmpy.web.views.new_project_view'),
    #url(r'^computing/create/user', 'qmpy.web.views.new_user_view'),
    #url(r'^computing/create/', 'qmpy.web.views.new_user_view'),

    url(r'^computing/project/(?P<state>.*)/(?P<project_id>.*)$', 'qmpy.web.views.project_state_view'),
    url(r'^computing/project/(?P<project_id>.*)$', 'qmpy.web.views.project_view'),
    url(r'^computing/host/(?P<host_id>.*)$', 'qmpy.web.views.host_view'),
    url(r'^computing/user/(?P<user_id>.*)$', 'qmpy.web.views.user_view'),
    url(r'^computing/allocation/(?P<allocation_id>.*)$', 'qmpy.web.views.allocation_view'),

    url(r'^computing/task/(?P<task_id>.*)$', 'qmpy.web.views.task_view'),
    url(r'^computing/job/(?P<job_id>.*)$', 'qmpy.web.views.job_view'),

    ## analysis
    url(r'^analysis/$', 'qmpy.web.views.analysis_view'),
    url(r'^analysis/gclp/$', 'qmpy.web.views.gclp_view'),
    url(r'^analysis/phase_diagram/$', 'qmpy.web.views.phase_diagram_view'),
    url(r'^analysis/chemical_potentials/$', 'qmpy.web.views.chem_pot_view'),
    url(r'^analysis/spacegroup/(?P<spacegroup>.*)', 'qmpy.web.views.sg_view'),
    url(r'^analysis/operation/(?P<operation>.*)', 'qmpy.web.views.op_view'),
    url(r'^analysis/visualize$', 'qmpy.web.views.vis_data'),
    url(r'^analysis/visualize/custom$', 'qmpy.web.views.jsmol'),

    ## documentation
    url(r'^documentation/$', 'qmpy.web.views.docs_view'),
    url(r'^documentation/vasp$', 'qmpy.web.views.vasp_docs'),
    url(r'^documentation/structures$', 'qmpy.web.views.structures_docs'), 
    url(r'^documentation/pots$', 'qmpy.web.views.pots_docs'),
    url(r'^documentation/overview$', 'qmpy.web.views.overview_docs'),
    url(r'^documentation/publications$', 'qmpy.web.views.pubs_docs'),

    ## api
    url(r'^api/$', 'qmpy.web.views.api_view'),
    url(r'^api/search', 'qmpy.web.views.search_data'),

    ## serializer
    url(r'^oqmdapi/entry$', views.EntryList.as_view()),
    url(r'^oqmdapi/entry/(?P<pk>[0-9]+)/$', views.EntryDetail.as_view()),
    url(r'^oqmdapi/calculation$', views.CalculationList.as_view()),
    url(r'^oqmdapi/calculation/(?P<pk>[0-9]+)/$', views.CalculationDetail.as_view()),
    url(r'^oqmdapi/formationenergy$', views.FormationEnergyList.as_view()),
    url(r'^oqmdapi/formationenergy/(?P<pk>[0-9]+)/$', views.FormationEnergyDetail.as_view()),

    ## optimade
    url(r'^optimade/structures$', views.OptimadeStructureList.as_view()),
    url(r'^optimade/structures/(?P<pk>[0-9]+)/$', views.OptimadeStructureDetail.as_view()),

    ## download
    url(r'^download/', 'qmpy.web.views.download_home'),

    ## other
    url(r'^faq', 'qmpy.web.views.faq_view'),
    url(r'^playground', 'qmpy.web.views.play_view')
]

