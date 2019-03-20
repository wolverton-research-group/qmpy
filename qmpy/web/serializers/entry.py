from rest_framework import serializers
from django.db.models import Q

from qmpy.materials.entry import Entry
from qmpy.materials.structure import Structure
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.analysis.vasp import Calculation

from calculation import CalculationRawSerializer

class EntrySerializer(serializers.ModelSerializer):
    composition = serializers.SerializerMethodField()
    composition_generic = serializers.SerializerMethodField()
    spacegroup = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()

    unit_cell = serializers.SerializerMethodField()
    sites = serializers.SerializerMethodField()

    energy_per_atom = serializers.SerializerMethodField()
    band_gap = serializers.SerializerMethodField()
    formation_energy = serializers.SerializerMethodField()

    stability = serializers.SerializerMethodField()

    calculations = serializers.SerializerMethodField('get_calc')

    def get_composition(self, entry):
        return entry.composition.formula

    def get_composition_generic(self, entry):
        return entry.composition.generic

    def get_spacegroup(self, entry):
        try:
            if 'static' in entry.structures:
                return entry.structures['static'].spacegroup.hm
            else:
                return entry.structures['input'].spacegroup.hm
        except:
            return 

    def get_volume(self, entry):
        try:
            if 'static' in entry.structures:
                return entry.structures['static'].volume
            else:
                return entry.structures['input'].volume
        except:
            return 

    def get_unit_cell(self, entry):
        try:
            if 'static' in entry.structures:
                strct = entry.structures['static']
            else:
                strct = entry.structures['input']

            return [[strct.x1, strct.x2, strct.x3],
                    [strct.y1, strct.y2, strct.y3],
                    [strct.z1, strct.z2, strct.z3]]
        except:
            return

    def get_sites(self, entry):
        try:
            if 'static' in entry.structures:
                strct = entry.structures['static']
            else:
                strct = entry.structures['input']

            sites = [str(s) for s in strct.sites]

            return sites
        except:
            return


    def get_energy_per_atom(self, entry):
        try:
            return entry.calculation_set.get(label='static', \
                                             converged=True).energy_pa
        except:
            try:
                return entry.calculation_set.get(label='standard', \
                                                 converged=True).energy_pa
            except:
                return 

    def get_band_gap(self, entry):
        try:
            return entry.calculation_set.get(label='static', \
                                             converged=True).band_gap
        except:
            try:
                return entry.calculation_set.get(label='standard', \
                                                 converged=True).band_gap
            except:
                return 

    def get_formation_energy(self, entry):
        try:
            return entry.formationenergy_set.get(fit_id='standard').delta_e
        except:
            return

    def get_stability(self, entry):
        try:
            return entry.formationenergy_set.get(fit_id='standard').stability
        except:
            return

    def get_calc(self, entry):
        qs = Calculation.objects.filter(converged=True, 
                                        entry=entry)
        serializer = CalculationRawSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Entry
        fields = ('id', 'name', 'path', 'composition', 'composition_generic', 
                  'prototype', 'spacegroup', 'volume',
                  'ntypes', 'natoms', 
                  'unit_cell', 'sites',
                  'energy_per_atom', 'band_gap', 
                  'formation_energy', 'stability',
                  'keywords', 'holds',
                  'calculations')
