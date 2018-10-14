from rest_framework import serializers
from qmpy.analysis.vasp import Calculation

class CalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calculation
        fields = ('id', 'entry', 'composition', 'path', 'label', 'band_gap', 'converged', 'energy_pa')

class CalculationRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calculation
        fields = ('id', 'path', 'label')
