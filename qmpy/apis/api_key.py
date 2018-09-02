import os
import binascii
from django.db import models

def generate_key():
    return binascii.hexlify(os.urandom(10)).decode()

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


    @staticmethod
    def create(username=None, email=None):
        if not username:
            username = raw_input("Username: ")
        if not email:
            email = raw_input("Email address: ")
        apiuser, new = APIKey.objects.get_or_create(username=username)
        if new:
            apiuser.email = email
            apiuser.key = generate_key()
            apiuser.save()
        return apiuser





