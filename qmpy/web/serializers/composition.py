from rest_framework import serializers
from qmpy.materials.composition import Composition


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ("formula", "generic")
