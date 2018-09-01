from django.db import models
from rest_framework import serializers
from qmpy.computing.resources import APIUser
from qmpy.materials.entry import Entry

#class UserSerializer(serializers.HyperlinkedModelSerializer):
class UserSerializer(serializers.ModelSerializer):
    #entries = serializers.PrimaryKeyRelatedField(many=True, queryset=Entry.objects.all()[:20])
    class Meta:
        model = APIUser
        fields = ('url', 'username', 'email')
        #fields = ('url', 'username', 'email', 'entries')

