from rest_framework import serializers
from qmpy.materials.formation_energy import FormationEnergy
from drf_queryfields import QueryFieldsMixin


class OptimadeStructureSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    chemical_formula_reduced = serializers.SerializerMethodField()
    chemical_formula_anonymous = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()
    nelements = serializers.SerializerMethodField()
    elements = serializers.SerializerMethodField()
    lattice_vectors = serializers.SerializerMethodField()
    cartesian_site_positions = serializers.SerializerMethodField()
    species_at_sites = serializers.SerializerMethodField()
    dimension_types = serializers.SerializerMethodField()
    nperiodic_dimensions = serializers.SerializerMethodField()
    elements_ratios = serializers.SerializerMethodField()
    structure_features = serializers.SerializerMethodField()
    chemical_formula_descriptive = serializers.SerializerMethodField()
    species = serializers.SerializerMethodField()

    _oqmd_icsd_id = serializers.SerializerMethodField()
    _oqmd_entry_id = serializers.SerializerMethodField()
    _oqmd_calculation_id = serializers.SerializerMethodField()

    _oqmd_direct_site_positions = serializers.SerializerMethodField()
    nsites = serializers.SerializerMethodField()
    _oqmd_spacegroup = serializers.SerializerMethodField()
    _oqmd_prototype = serializers.SerializerMethodField()

    _oqmd_band_gap = serializers.SerializerMethodField()
    _oqmd_delta_e = serializers.SerializerMethodField()
    _oqmd_stability = serializers.SerializerMethodField()
    _oqmd_volume = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(OptimadeStructureSerializer, self).__init__(*args, **kwargs)
        request = self.context["request"]
        query_params = request.query_params
        _fields = query_params.getlist("fields")
        if not _fields:
            fields_to_drop = {
                "chemical_formula_descriptive",
                "elements_ratios",
                "dimension_types",
                "_oqmd_direct_site_positions",
                "nperiodic_dimensions",
                "species",
            }
            for field in fields_to_drop:
                self.fields.pop(field)

    # Mandatory properties
    def get_type(self, _):
        return "structures"

    def get_last_modified(self, _):
        return ""

    # Optimade recommended structure-related properties
    def get_chemical_formula_reduced(self, formationenergy):
        # Remove spaces and remove "1" from composition, e.g. O2 Si1 -> O2Si
        formula = formationenergy.composition.formula.split()
        for ind, species in enumerate(formula):
            if species[-1] == "1" and species[-2].isalpha():
                formula[ind] = species[:-1]

        return "".join(formula)

    def get_chemical_formula_anonymous(self, formationenergy):
        return formationenergy.composition.generic

    def get_nelements(self, formationenergy):
        return formationenergy.composition.ntypes

    def get_elements(self, formationenergy):
        elst = formationenergy.composition.element_list.split("_")
        elst.pop()
        return ",".join(elst)

    def get_lattice_vectors(self, formationenergy):
        try:
            strct = formationenergy.calculation.output

            return [
                [strct.x1, strct.x2, strct.x3],
                [strct.y1, strct.y2, strct.y3],
                [strct.z1, strct.z2, strct.z3],
            ]
        except:
            return []

    def get_nsites(self, formationenergy):
        return formationenergy.entry.natoms

    def get_species_at_sites(self, formationenergy):
        try:
            strct = formationenergy.calculation.output
            sites = [s.label for s in strct.sites]
            return sites
        except:
            return []

    def get_cartesian_site_positions(self, formationenergy):
        try:
            strct = formationenergy.calculation.output
            sites = [s.atoms[0].cart_coord.round(6).tolist() for s in strct.sites]
            return sites
        except:
            return []

    def get__oqmd_direct_site_positions(self, formationenergy):
        try:
            strct = formationenergy.calculation.output
            sites = [s.coord.round(6).tolist() for s in strct.sites]
            return sites
        except:
            return []

    # Constant value or unsupported properties, but response required by optimade
    def get_dimension_types(self, _):
        return [1, 1, 1]

    def get_nperiodic_dimensions(self, _):
        return 3

    def get_elements_ratios(self, _):
        return []

    def get_structure_features(self, _):
        return []

    def get_chemical_formula_descriptive(self, _):
        return ""

    def get_species(self, _):
        return []

    # OQMD specific data
    def get__oqmd_icsd_id(self, formationenergy):
        entry = formationenergy.entry
        if "icsd" in entry.keywords:
            try:
                assert "icsd" in entry.path
                return int(entry.path.split("/")[-1])
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

    def get__oqmd_band_gap(self, formationenergy):
        return formationenergy.calculation.band_gap

    def get__oqmd_delta_e(self, formationenergy):
        return round(formationenergy.delta_e, 4)

    def get__oqmd_stability(self, formationenergy):
        if formationenergy.stability is not None:
            return max(round(formationenergy.stability, 3), 0.0)
        else:
            return

    def get__oqmd_volume(self, formationenergy):
        return formationenergy.calculation.output.volume

    class Meta:
        model = FormationEnergy
        fields = (
            "id",
            "type",
            "last_modified",
            "chemical_formula_reduced",
            "chemical_formula_anonymous",
            "nelements",
            "elements",
            "nsites",
            "lattice_vectors",
            "_oqmd_direct_site_positions",
            "species_at_sites",
            "dimension_types",
            "nperiodic_dimensions",
            "elements_ratios",
            "structure_features",
            "chemical_formula_descriptive",
            "species",
            "cartesian_site_positions",
            "_oqmd_entry_id",
            "_oqmd_calculation_id",
            "_oqmd_icsd_id",
            "_oqmd_band_gap",
            "_oqmd_delta_e",
            "_oqmd_volume",
            "_oqmd_stability",
            "_oqmd_prototype",
            "_oqmd_spacegroup",
        )
