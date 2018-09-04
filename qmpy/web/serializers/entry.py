from rest_framework import serializers
from qmpy.materials.entry import Entry
from calculation import CalculationSerializer

class EntrySerializer(serializers.ModelSerializer):
    calculations = CalculationSerializer(source='calculation_set', many=True, read_only=True)

    class Meta:
        model = Entry
        fields = ('id', 'path', 'natoms', 'energy', 'calculations')
