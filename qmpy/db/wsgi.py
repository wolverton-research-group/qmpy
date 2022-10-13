import os, os.path
import sys
import site
import django
import qmpy

INSTALL_DIR = os.path.abspath(__file__).replace("/qmpy/db/wsgi.py", "")

os.environ["HOME"] = "/dev/shm"

# # Add the app's directory to the PYTHONPATH
sys.path.append(INSTALL_DIR + "/qmpy/db")
sys.path.append(INSTALL_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qmpy.db.settings")

from django.conf import settings

if not settings.configured:
    settings.configure(default_settings=qmpy.db.settings, DEBUG=False)
django.setup()

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
