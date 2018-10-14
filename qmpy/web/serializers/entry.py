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
    energy_per_atom_hse = serializers.SerializerMethodField()

    band_gap = serializers.SerializerMethodField()
    band_gap_hse = serializers.SerializerMethodField()
    
    formation_energy = serializers.SerializerMethodField()
    formation_energy_hse = serializers.SerializerMethodField()

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
            if entry.calculations['static'].converged:
                return entry.calculations['static'].energy_pa
            else:
                return
        except:
            return 

    def get_energy_per_atom_hse(self, entry):
        try:
            if entry.calculations['hse06'].converged:
                return entry.calculations['hse06'].energy_pa
            else:
                return
        except:
            return 

    def get_band_gap(self, entry):
        try:
            if entry.calculations['static'].converged:
                return entry.calculations['static'].band_gap
            else:
                return
        except:
            return 

    def get_band_gap_hse(self, entry):
        try:
            if entry.calculations['hse06'].converged:
                return entry.calculations['hse06'].band_gap
            else:
                return
        except:
            return 

    def get_formation_energy(self, entry):
        try:
            static_id = entry.calculations['static'].id
            return entry.formationenergy_set.get(calculation_id=static_id).delta_e
        except:
            return

    def get_formation_energy_hse(self, entry):
        try:
            hse_id = entry.calculations['hse06'].id
            return entry.formationenergy_set.get(calculation_id=hse_id).delta_e
        except:
            return

    def get_stability(self, entry):
        try:
            static_id = entry.calculations['static'].id
            return entry.formationenergy_set.get(calculation_id=static_id).stability
        except:
            return

    def get_calc(self, entry):
        qs = Calculation.objects.filter(converged=True, 
                                        #label__in=['static', 'hse06'], 
                                        entry=entry)
        serializer = CalculationRawSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Entry
        fields = ('id', 'name', 'path', 'composition', 'composition_generic', 
                  'prototype', 'spacegroup', 'volume',
                  'ntypes', 'natoms', 
                  'unit_cell', 'sites',
                  'energy_per_atom', 'energy_per_atom_hse',
                  'band_gap', 'band_gap_hse',
                  'formation_energy', 'formation_energy_hse', 'stability',
                  'keywords', 'holds',
                  'calculations')
