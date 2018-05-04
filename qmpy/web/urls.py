from django.conf.urls import patterns, include, url

import django.views.generic
from django.views.generic import DetailView, ListView
from django.contrib import admin
from qmpy.db import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'qmpy.web.views.home_page'),

    ## admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/login/.*$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/.*$', 'django.contrib.auth.views.logout'),
    url(r'^admin/', include(admin.site.urls)))

urlpatterns += patterns('qmpy.web.views',
    ## materials
    url(r'^materials/$', 'composition_view'),
    url(r'^materials/structure/(?P<structure_id>.*)$', 'structure_view'),
    url(r'^materials/composition/(?P<search>.*)$', 'composition_view'),
    url(r'^materials/entry/(?P<entry_id>.*)$', 'entry_view'),
    url(r'^materials/duplicates/(?P<entry_id>.*)$', 'duplicate_view'),
    url(r'^materials/prototype/(?P<name>.*)$', 'prototype_view'),
    url(r'^materials/prototypes$', 'prototypes_view'),
    url(r'^materials/keyword/(?P<keyword>.*)$', 'keyword_view'),
    url(r'^materials/generic_composition/(?P<search>.*)$', 'generic_composition_view'),

    url(r'^materials/export/(?P<convention>.*)/(?P<format>.*)/(?P<structure_id>.*)',
        'export_structure'),
    url(r'^materials/export/(?P<format>.*)/(?P<structure_id>.*)', 'export_structure'),
    url(r'^materials/export/(?P<convention>.*)/(?P<structure_id>.*)', 'export_structure'),
    url(r'^materials/export/(?P<structure_id>.*)', 'export_structure'),
    url(r'^materials/xrd/(?P<structure_id>.*).csv', 'export_xrd'),
    url(r'^materials/kpoints/(?P<mesh>.*)/(?P<structure_id>.*)/KPOINTS',
        'export_kpoints'),
    url(r'^materials/discovery', 'disco_view'),
    url(r'^materials/chempots', 'chem_pot_view'),
    url(r'^materials/deposit', 'deposit_view'),

    ## References
    url(r'^reference/author/(?P<author_id>.*)$', 'author_view'),
    url(r'^reference/journal/(?P<journal_id>.*)$', 'journal_view'),
    url(r'^reference/(?P<reference_id>.*)$', 'reference_view'),

    ## calculations
    url(r'^analysis/calculation/(?P<calculation_id>.*)$', 'calculation_view'),

    ## computing
    url(r'^computing/$', 'computing_view'),
    url(r'^computing/projects$', 'projects_view'),
    url(r'^computing/hosts$', 'hosts_view'),
    url(r'^computing/queue$', 'queue_view'),

    url(r'^computing/create/host$', 'new_host_view'),
    url(r'^computing/create/project', 'new_project_view'),
    url(r'^computing/create/user', 'new_user_view'),
    url(r'^computing/create/', 'new_user_view'),

    url(r'^computing/project/(?P<state>.*)/(?P<project_id>.*)$', 'project_state_view'),
    url(r'^computing/project/(?P<project_id>.*)$', 'project_view'),
    url(r'^computing/host/(?P<host_id>.*)$', 'host_view'),
    url(r'^computing/user/(?P<user_id>.*)$', 'user_view'),
    url(r'^computing/allocation/(?P<allocation_id>.*)$', 'allocation_view'),

    url(r'^computing/task/(?P<task_id>.*)$', 'task_view'),
    url(r'^computing/job/(?P<job_id>.*)$', 'job_view'),
    url(r'^computing/onlinesubmit$', 'online_view'),

    ## analysis
    url(r'^analysis/$', 'analysis_view'),
    url(r'^analysis/gclp/$', 'gclp_view'),
    url(r'^analysis/phase_diagram/$', 'phase_diagram_view'),
    url(r'^analysis/chemical_potentials/$', 'chem_pot_view'),
    url(r'^analysis/spacegroup/(?P<spacegroup>.*)', 'sg_view'),
    url(r'^analysis/operation/(?P<operation>.*)', 'op_view'),
    url(r'^analysis/visualize$', 'vis_data'),
    url(r'^analysis/visualize/custom$', 'jsmol'),

    ## documentation
    url(r'^documentation/$', 'docs_view'),
    url(r'^documentation/vasp$', 'vasp_docs'),
    url(r'^documentation/structures$', 'structures_docs'), 
    url(r'^documentation/pots$', 'pots_docs'),
    url(r'^documentation/overview$', 'overview_docs'),
    url(r'^documentation/publications$', 'pubs_docs'),

    ## download
    url(r'^download/', 'download_home'),

    ## other
    url(r'^faq', 'faq_view'),
    url(r'^playground', 'play_view'),
)
