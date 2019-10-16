from rest_framework import serializers
from qmpy.materials.formation_energy import FormationEnergy
from drf_queryfields import QueryFieldsMixin

class OptimadeStructureSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    chemical_formula = serializers.SerializerMethodField()
    formula_prototype = serializers.SerializerMethodField()
    elements = serializers.SerializerMethodField()
    nelements = serializers.SerializerMethodField()

    _oqmd_icsd_id = serializers.SerializerMethodField()
    _oqmd_entry_id = serializers.SerializerMethodField()
    _oqmd_calculation_id = serializers.SerializerMethodField()

    _oqmd_unit_cell = serializers.SerializerMethodField()
    _oqmd_sites = serializers.SerializerMethodField()
    _oqmd_natoms = serializers.SerializerMethodField()
    _oqmd_spacegroup = serializers.SerializerMethodField()
    _oqmd_prototype = serializers.SerializerMethodField()

    _oqmd_band_gap = serializers.SerializerMethodField()
    _oqmd_delta_e = serializers.SerializerMethodField()
    _oqmd_stability = serializers.SerializerMethodField()


    def get_chemical_formula(self, formationenergy):
        return formationenergy.composition.formula.replace(' ','')
    
    def get_formula_prototype(self, formationenergy):
        return formationenergy.composition.generic

    def get_nelements(self, formationenergy):
        return formationenergy.composition.ntypes

    def get_elements(self, formationenergy):
        elst = formationenergy.composition.element_list.split('_')
        elst.pop()
        return ','.join(elst)

    def get__oqmd_icsd_id(self, formationenergy):
        entry = formationenergy.entry
        if 'icsd' in entry.keywords:
            try:
                assert 'icsd' in entry.path
                return int(entry.path.split('/')[-1])
            except:
                pass

    def get__oqmd_entry_id(self, formationenergy):
        return formationenergy.entry.id

    def get__oqmd_calculation_id(self, formationenergy):
        return formationenergy.calculation.id
    
    def get__oqmd_spacegroup(self, formationenergy):
        try:
            return formationenergy.calculation.output.spacegroup.hm
        except AttributeError:
            return

    def get__oqmd_prototype(self, formationenergy):
        try:
            return formationenergy.entry.prototype.name
        except:
            return

    def get__oqmd_unit_cell(self, formationenergy):
        try:
            strct = formationenergy.calculation.output

            return [[strct.x1, strct.x2, strct.x3],
                    [strct.y1, strct.y2, strct.y3],
                    [strct.z1, strct.z2, strct.z3]]
        except:
            return

    def get__oqmd_sites(self, formationenergy):
        try:
            strct = formationenergy.calculation.output
            sites = [str(s) for s in strct.sites]

            return sites
        except:
            return

    def get__oqmd_natoms(self, formationenergy):
        return formationenergy.entry.natoms

    def get__oqmd_band_gap(self, formationenergy):
        return formationenergy.calculation.band_gap

    def get__oqmd_delta_e(self, formationenergy):
        return formationenergy.delta_e

    def get__oqmd_stability(self, formationenergy):
        if formationenergy.stability is not None:
            return max(formationenergy.stability, 0.0)
        else:
            return

    class Meta:
        model = FormationEnergy
        fields = ('id',
                  'nelements', 'elements', 
                  'chemical_formula', 'formula_prototype', 
                  '_oqmd_entry_id', '_oqmd_calculation_id','_oqmd_icsd_id',
                  '_oqmd_band_gap', '_oqmd_delta_e', '_oqmd_stability',
                  '_oqmd_prototype', '_oqmd_spacegroup', '_oqmd_natoms',
                  '_oqmd_unit_cell', '_oqmd_sites')
