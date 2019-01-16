"""qmpy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from rest_framework import routers

#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)

import qmpy.web.views as views

urlpatterns = [
    url(r'^$', views.home_page),

    ## admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/login/.*$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/.*$', 'django.contrib.auth.views.logout'),
    url(r'^admin/', include(admin.site.urls)),

    ## api
#    url(r'^api_login/', include(router.urls)),
#    url(r'^api_auth/', include('rest_framework.urls', namespace='rest_framework'))
    # TODO: remove code related to admin interface from qmpy
    url(r'^admin/', admin.site.urls),
    ]

urlpatterns += [
    ## materials
    url(r'^materials/$', views.composition_view),
    url(r'^materials/structure/(?P<structure_id>.*)$', views.structure_view),
    url(r'^materials/composition/(?P<search>.*)$', views.composition_view),
    url(r'^materials/entry/(?P<entry_id>.*)$', views.entry_view),
    url(r'^materials/duplicates/(?P<entry_id>.*)$', views.duplicate_view),
    url(r'^materials/prototype/(?P<name>.*)$', views.prototype_view),
    url(r'^materials/prototypes$', views.prototypes_view),
    url(r'^materials/keyword/(?P<keyword>.*)$', views.keyword_view),
    url(r'^materials/generic_composition/(?P<search>.*)$', views.generic_composition_view),

    url(r'^materials/export/(?P<convention>.*)/(?P<format>.*)/(?P<structure_id>.*)',
        views.export_structure),
    url(r'^materials/export/(?P<format>.*)/(?P<structure_id>.*)', views.export_structure),
    url(r'^materials/export/(?P<convention>.*)/(?P<structure_id>.*)', views.export_structure),
    url(r'^materials/export/(?P<structure_id>.*)', views.export_structure),
    url(r'^materials/xrd/(?P<structure_id>.*).csv', views.export_xrd),
    url(r'^materials/kpoints/(?P<mesh>.*)/(?P<structure_id>.*)/KPOINTS',
        views.export_kpoints),
    url(r'^materials/discovery', views.disco_view),
    url(r'^materials/chem_pots', views.chem_pot_view),
    url(r'^materials/deposit', views.deposit_view),

    ## References
    url(r'^reference/author/(?P<author_id>.*)$', views.author_view),
    url(r'^reference/journal/(?P<journal_id>.*)$', views.journal_view),
    url(r'^reference/(?P<reference_id>.*)$', views.reference_view),

    ## calculations
    url(r'^analysis/calculation/(?P<calculation_id>.*)$', views.calculation_view),

    ## computing
    url(r'^computing/$', views.computing_view),
    url(r'^computing/projects$', views.projects_view),
    url(r'^computing/hosts$', views.hosts_view),
    url(r'^computing/queue$', views.queue_view),

    url(r'^computing/create/host$', views.new_host_view),
    url(r'^computing/create/project', views.new_project_view),

    url(r'^computing/project/(?P<state>.*)/(?P<project_id>.*)$', views.project_state_view),
    url(r'^computing/project/(?P<project_id>.*)$', views.project_view),
    url(r'^computing/host/(?P<host_id>.*)$', views.host_view),
    url(r'^computing/user/(?P<user_id>.*)$', views.user_view),
    url(r'^computing/allocation/(?P<allocation_id>.*)$', views.allocation_view),

    url(r'^computing/task/(?P<task_id>.*)$', views.task_view),
    url(r'^computing/job/(?P<job_id>.*)$', views.job_view),

    ## analysis
    url(r'^analysis/$', views.analysis_view),
    url(r'^analysis/gclp/$', views.gclp_view),
    url(r'^analysis/phase_diagram/$', views.phase_diagram_view),
    url(r'^analysis/chemical_potentials/$', views.chem_pot_view),
    url(r'^analysis/spacegroup/(?P<spacegroup>.*)', views.sg_view),
    url(r'^analysis/operation/(?P<operation>.*)', views.op_view),
    url(r'^analysis/visualize$', views.vis_data),
    url(r'^analysis/visualize/custom$', views.jsmol),

    ## documentation
    url(r'^documentation/$', views.docs_view),
    url(r'^documentation/vasp$', views.vasp_docs),
    url(r'^documentation/structures$', views.structures_docs),
    url(r'^documentation/pots$', views.pots_docs),
    url(r'^documentation/overview$', views.overview_docs),
    url(r'^documentation/publications$', views.pubs_docs),

    ## api
    url(r'^api/$', 'qmpy.web.views.api_view'),
    url(r'^api/register', 'qmpy.web.views.api_key_gen'),
    url(r'^api/search', 'qmpy.web.views.search_data'),

    ## serializer
    url(r'^serializer/entry$', views.EntryList.as_view()),
    url(r'^serializer/entry/(?P<pk>[0-9]+)/$', views.EntryDetail.as_view()),
    url(r'^serializer/calculation$', views.CalculationList.as_view()),
    url(r'^serializer/calculation/(?P<pk>[0-9]+)/$', views.CalculationDetail.as_view()),

    ## download
    url(r'^download/', views.download_home),

    ## other
    url(r'^faq', views.faq_view),
    url(r'^playground', views.play_view),
]

