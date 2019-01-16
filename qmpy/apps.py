# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class qmpyConfig(AppConfig):
    name = 'qmpy'

    def ready(self):
        from .models import *
