from rest_framework import serializers
from qmpy.materials.formation_energy import FormationEnergy

class FormationEnergySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    entry_id = serializers.SerializerMethodField()
    calculation_id = serializers.SerializerMethodField()
    calculation_label = serializers.SerializerMethodField()
    formationenergy_id = serializers.SerializerMethodField()
    icsd_id = serializers.SerializerMethodField()

    composition = serializers.SerializerMethodField()
    composition_generic = serializers.SerializerMethodField()
    spacegroup = serializers.SerializerMethodField()
    prototype = serializers.SerializerMethodField()
    
    volume = serializers.SerializerMethodField()
    unit_cell = serializers.SerializerMethodField()
    sites = serializers.SerializerMethodField()

    ntypes = serializers.SerializerMethodField()
    natoms = serializers.SerializerMethodField()

    band_gap = serializers.SerializerMethodField()

    def get_name(self, formationenergy):
        return formationenergy.entry.name

    def get_entry_id(self, formationenergy):
        return formationenergy.entry.id

    def get_calculation_id(self, formationenergy):
        return formationenergy.calculation.id

    def get_calculation_label(self, formationenergy):
        return formationenergy.calculation.label

    def get_icsd_id(self, formationenergy):
        entry = formationenergy.entry
        if 'icsd' in entry.keywords:
            try:
                assert 'icsd' in entry.path
                return int(entry.path.split('/')[-1])
            except:
                pass

    def get_formationenergy_id(self, formationenergy):
        return formationenergy.id

    def get_composition(self, formationenergy):
        return formationenergy.composition.formula
    
    def get_composition_generic(self, formationenergy):
        return formationenergy.composition.generic
    
    def get_spacegroup(self, formationenergy):
        return formationenergy.calculation.output.spacegroup.hm

    def get_prototype(self, formationenergy):
        try:
            return formationenergy.entry.prototype.name
        except:
            return

    def get_volume(self, formationenergy):
        return formationenergy.calculation.output.volume

    def get_unit_cell(self, formationenergy):
        try:
            strct = formationenergy.calculation.output

            return [[strct.x1, strct.x2, strct.x3],
                    [strct.y1, strct.y2, strct.y3],
                    [strct.z1, strct.z2, strct.z3]]
        except:
            return

    def get_sites(self, formationenergy):
        try:
            strct = formationenergy.calculation.output
            sites = [str(s) for s in strct.sites]

            return sites
        except:
            return

    def get_ntypes(self, formationenergy):
        return formationenergy.entry.ntypes

    def get_natoms(self, formationenergy):
        return formationenergy.entry.natoms

    def get_band_gap(self, formationenergy):
        return formationenergy.calculation.band_gap

    class Meta:
        model = FormationEnergy
        fields = ('name', 'entry_id', 'calculation_id', 
                  'icsd_id', 'formationenergy_id',
                  'composition', 'composition_generic', 
                  'prototype', 'spacegroup', 'volume', 
                  'ntypes', 'natoms', 
                  'unit_cell', 'sites', 'band_gap', 
                  'delta_e', 'stability', 'fit', 'calculation_label')
