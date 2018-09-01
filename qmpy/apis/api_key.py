import os
from django.db import models

class APIKey(models.Model):
    username = models.CharField(max_length=255, null=False, blank=False, db_index=True)
    email = models.EmailField(max_length=254, null=False, blank=True)

    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'apikeys'

    def __str__(self):
        return self.username

