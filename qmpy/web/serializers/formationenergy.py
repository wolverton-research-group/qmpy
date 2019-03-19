from rest_framework import serializers
from qmpy.materials.formation_energy import FormationEnergy

class FormationEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationEnergy
        fields = ('calculation', 'fit', 'delta_e', 'stability')
