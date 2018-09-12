from rest_framework import serializers
from qmpy.materials.entry import Entry
from qmpy.analysis.vasp import Calculation
from calculation import CalculationSerializer

class EntrySerializer(serializers.ModelSerializer):
    calculations = serializers.SerializerMethodField('get_calc')

    def get_calc(self, entry):
        qs = Calculation.objects.filter(converged=True, 
                                        label__in=['static', 'hse06'], 
                                        entry=entry)
        serializer = CalculationSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Entry
        fields = ('id', 'name', 'composition', 'natoms', 'energy', 'calculations')
