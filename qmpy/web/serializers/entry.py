from rest_framework import serializers
from qmpy.materials.entry import Entry

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('id', 'path', 'natoms')
