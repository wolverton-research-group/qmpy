from rest_framework import serializers
from qmpy.materials.structure import Structure


class StructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Structure
        fields = ("spacegroup", "x1", "x2", "x3", "y1", "y2", "y3")
