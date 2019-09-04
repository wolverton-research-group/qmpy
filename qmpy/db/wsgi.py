import os, os.path
import sys
import site

INSTALL_DIR = os.path.abspath(__file__).replace('/qmpy/db/wsgi.py', '')

os.environ['HOME'] = '/dev/shm'
import matplotlib
matplotlib.use('Agg')
import matplotlib.cbook

# # Add the app's directory to the PYTHONPATH
sys.path.append(INSTALL_DIR+'/qmpy/db')
sys.path.append(INSTALL_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qmpy.db.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
