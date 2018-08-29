from django.contrib.auth.models import Group
from django.db import models
from rest_framework import serializers
from qmpy.computing.resources import APIUser

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = APIUser
        fields = ('url', 'username', 'email')	

#class GroupSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = Group
#        fields = ('url', 'name')
