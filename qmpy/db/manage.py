#!/usr/bin/env python
import os, sys
from os.path import dirname, abspath
import matplotlib
matplotlib.use('Agg')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qmpy.db.settings")

    from django.core.management import execute_from_command_line
    
    execute_from_command_line(sys.argv)
