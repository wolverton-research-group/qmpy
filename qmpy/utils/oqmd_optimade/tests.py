from qmpy.utils import *
from django.test import SimpleTestCase
from django.db.models import Q
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from types import SimpleNamespace
import numpy as np

from qmpy.web.serializers.optimade import OptimadeStructureSerializer
from qmpy.utils.oqmd_optimade.QueryLarkDjangoParser import (
    NotImplementedErr,
    LarkParserError,
)

# At some point, we need to run OPTIMADE Validatior Action tests
# in qmpy Github Actions, instead of doing these tests - Abi


class RESTfulTestCase(SimpleTestCase):
    def setUp(self):
        self.transformer = Lark2Django()

    def transform_q(self, query, return_mode=0):
        """
        Three return modes are available as of now

        return_mode=0 : Returns the default string representation of final Django query
        return_mode=1 : Returns the warnings-list from the parser
        return_mode=2 : Returns the custom string representation of final Django query
        return_mode=3 : Returns the exception received from transformer
        """
        self.transformer = Lark2Django()
        tree = self.transformer.parse_raw_q(query)
        if return_mode == 0:
            return self.transformer.evaluate(tree)[0].__str__()
        elif return_mode == 1:
            return self.transformer.evaluate(tree)[1]["warnings"]
        elif return_mode == 2:
            return self.transformer.evaluate(tree)[1]["django_query"]
        elif return_mode == 3:
            _0, _1 = self.transformer.evaluate(tree)

    def test_djangoQ_printer(self):
        truth_value = "(((NOT( stability__gt=0 )) AND ( calculation__band_gap__gt=2  OR  composition__element_list__contains=Fe_  OR  composition__element_list__contains=Mn_ )) OR ( calculation__band_gap__gt=2  AND ((NOT( composition__generic=AB )) OR  calculation__output__spacegroup__hm=Fm-3m )))"
        assert truth_value == self.transform_q(
            'NOT _oqmd_stability>0 AND (_oqmd_band_gap>2 OR elements HAS ANY "Fe","Mn") OR (_oqmd_band_gap>2 AND (NOT chemical_formula_anonymous="AB" OR _oqmd_spacegroup="Fm-3m"))',
            2,
        )

    def test_queries(self):

        # Testing numerical value parsing
        truth_value = "(OR: (AND: ('stability', '0'), ('calculation__band_gap__gt', '0.5')), ('calculation__output__volume__gt', '1.4e+2'))"
        assert truth_value == self.transform_q(
            "_oqmd_stability=0     AND _oqmd_band_gap>0.5 OR _oqmd_volume>1.4e+2", 0
        )
        assert truth_value == self.transform_q(
            "_oqmd_stability=0AND_oqmd_band_gap>0.5OR_oqmd_volume>1.4e+2", 0
        )
        assert truth_value == self.transform_q(
            "_oqmd_stability=0 AND _oqmd_band_gap>0.5 OR _oqmd_volume>1.4e+2", 0
        )

        # Testing standard OPTIMADE and namespaced OQMD property names
        truth_value = "(OR: ('entry__composition__ntypes__lte', '3'), ('entry__composition__ntypes__gt', '5'))"
        assert truth_value == self.transform_q("nelements<=3 OR nelements>5")
        truth_value = "(OR: ('stability__lte', '-0.2'), ('stability__gt', '1.'))"
        assert truth_value == self.transform_q(
            "_oqmd_stability<=-0.2 OR _oqmd_stability>1."
        )
        truth_value = "(OR: ('entry__composition__ntypes', '3'), ('entry__composition__ntypes', '5'))"
        assert truth_value == self.transform_q("elements LENGTH 3 OR nelements=5")

        # Queries with HAS and such other newer operator typrs
        truth_value = "(AND: ('composition__element_list__contains', 'Al_'))"
        assert truth_value == self.transform_q('elements HAS "Al"')
        truth_value = "(AND: ('composition__element_list__contains', 'Al_'), ('composition__element_list__contains', 'B_'))"
        assert truth_value == self.transform_q('elements HAS ALL "Al","B"')
        truth_value = "(OR: ('composition__element_list__contains', 'Al_'), ('composition__element_list__contains', 'B_'))"
        assert truth_value == self.transform_q('elements HAS ANY "Al","B"')
        truth_value = "(AND: ('composition__element_list__contains', 'Al_'), ('composition__element_list__contains', 'B_'), ('entry__composition__ntypes', 2))"
        assert truth_value == self.transform_q('elements HAS ONLY "Al","B"')
        truth_value = "(AND: ('entry__composition__ntypes', '3'))"
        assert truth_value == self.transform_q("elements LENGTH 3")

        # queries that return None. i.e; no data is returned but a BadRequest400 error is not raised.
        # A Django query to return no values is executed in this case
        truth_value = "(AND: ('id', -1))"
        assert truth_value == self.transform_q("_abc_elements LENGTH 3")

        # Other property-dependant tests
        truth_value = "(AND: ('id', '1234'))"
        assert truth_value == self.transform_q('id="1234"')
        truth_value = "(AND: ('composition__formula__in', ['Al2 O3']))"
        assert truth_value == self.transform_q('chemical_formula_reduced="Al2O3"')
        truth_value = "(AND: ('composition__formula__in', ['Co1 O3', 'Cr1 O3', 'Cu1 O3', 'Fe1 O3', 'Mn1 O3', 'Ni1 O3', 'O3 Sc1', 'O3 Ti1', 'O3 V1', 'O3 Zn1']))"
        assert truth_value == self.transform_q('chemical_formula_reduced="{3d}O3"')

        # Miscellaneous Tests
        truth_value = "(NOT (AND: ('stability__gt', '3')))"
        assert truth_value == self.transform_q("NOT _oqmd_stability > 3")
        truth_value = "(OR: (AND: (NOT (AND: ('stability__gt', '0'))), (OR: ('calculation__band_gap__gt', '2'), ('composition__element_list__contains', 'Fe_'), ('composition__element_list__contains', 'Mn_'))), (AND: ('calculation__band_gap__gt', '2'), (OR: (NOT (AND: ('composition__generic', 'AB'))), ('calculation__output__spacegroup__hm', 'Fm-3m'))))"
        assert truth_value == self.transform_q(
            'NOT _oqmd_stability>0 AND (_oqmd_band_gap>2 OR elements HAS ANY "Fe","Mn") OR (_oqmd_band_gap>2 AND (NOT chemical_formula_anonymous="AB" OR _oqmd_spacegroup="Fm-3m"))'
        )
        truth_value = "(AND: ('composition__formula__in', ['Al1']))"
        assert truth_value == self.transform_q('chemical_formula_reduced= "   Al "')
        truth_value = "(AND: ('entry__natoms__lt', '8'), ('id', -1))"
        assert truth_value == self.transform_q("nsites<8 AND _abc_stability<0")
        truth_value = "(AND: ('id', '112/23344'))"
        assert truth_value == self.transform_q('id="112/23344"')

    def test_errors(self):
        self.assertRaises(
            LarkParserError, self.transform_q, "abc_elements LENGTH 3", 3
        )
        self.assertRaises(LarkParserError, self.transform_q, "xyz = 3", 3)
        self.assertRaises(
            LarkParserError,
            self.transform_q,
            "abcd=0 AND _oqmd_band_gap>0 OR lattice_vectors=12345",
            3,
        )
        self.assertRaises(
            LarkParserError,
            self.transform_q,
            "_oqmd_stability>0 OR NOT lattice_vectors>12345",
            3,
        )
        self.assertRaises(NotImplementedErr, self.transform_q, 'elements HAS "A"', 3)
        self.assertRaises(
            LarkParserError, self.transform_q, 'elements HAS ANY "Al",D', 3
        )
        self.assertRaises(LarkParserError, self.transform_q, "elements HAS Al", 3)
        self.assertRaises(LarkParserError, self.transform_q, "id=112/23344", 3)
        self.assertRaises(NotImplementedErr, self.transform_q, "elements LENGTH > 3", 3)
        self.assertRaises(
            NotImplementedErr, self.transform_q, "_oqmd_stability HAS 1", 3
        )
        self.assertRaises(LarkParserError, self.transform_q, "OR stability > 3", 3)
        self.assertRaises(LarkParserError, self.transform_q, "NOT abcd > 3", 3)
        self.assertRaises(LarkParserError, self.transform_q, "AND", 3)
        self.assertRaises(
            LarkParserError, self.transform_q, "chemical_formula_reduced=Al2O3", 3
        )
        self.assertRaises(
            NotImplementedErr, self.transform_q, 'chemical_formula_reduced="{4z}"', 3
        )
        self.assertRaises(
            NotImplementedErr, self.transform_q, 'elements HAS "   Al "', 3
        )
        self.assertRaises(LarkParserError, self.transform_q, " < 0", 3)
        self.assertRaises(LarkParserError, self.transform_q, "AND < 0", 3)
        self.assertRaises(LarkParserError, self.transform_q, " < 0", 3)

    def test_v1_3_property_semantics(self):
        self.assertEqual((1, 2, 0), self.transformer.parser.version)
        self.assertEqual("(AND: )", self.transform_q('type="structures"'))
        self.assertEqual("(AND: ('id', -1))", self.transform_q('type!="structures"'))
        self.assertEqual("(AND: )", self.transform_q("last_modified IS UNKNOWN"))
        self.assertEqual(
            "(AND: ('id', -1))", self.transform_q("last_modified IS KNOWN")
        )
        self.assertEqual("(AND: )", self.transform_q("_abc_missing IS UNKNOWN"))
        self.assertEqual("(AND: ('id', -1))", self.transform_q("_abc_flag=TRUE"))
        self.assertRaises(LarkParserError, self.transform_q, "_ < 0", 3)

    def test_warnings(self):
        assert self.transform_q("_abc_stability < 0", 1)[0]["detail"].startswith(
            "_oqmd_GeneralWarning"
        )
        assert self.transform_q("nsites<8 AND _abc_missing<0", 1)[0]["detail"].startswith(
            "_oqmd_GeneralWarning"
        )
        assert self.transform_q("nsites<8 AND nelements<4", 1) == []


class OptimadeEndpointTestCase(SimpleTestCase):
    def test_info_advertises_v1_3(self):
        response = self.client.get("/optimade/info")
        self.assertEqual(response.status_code, 200)
        document = response.json()
        self.assertEqual(document["meta"]["api_version"], "1.3.0")
        self.assertEqual(document["data"]["attributes"]["formats"], ["json"])
        self.assertEqual(
            document["data"]["attributes"]["available_api_versions"][0][
                "version"
            ],
            "1.3.0",
        )

    def test_versioned_info_uses_versioned_query_representation(self):
        response = self.client.get("/optimade/v1/info")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["query"]["representation"], "/info")

    def test_versions_is_csv(self):
        response = self.client.get("/optimade/versions")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertEqual(response.content.decode(), "version\n1\n")

    def test_unsupported_version_is_optimade_error(self):
        response = self.client.get("/optimade/v2/info")
        self.assertEqual(response.status_code, 553)
        self.assertEqual(response.json()["errors"][0]["code"], "VersionNotSupported")

    def test_unrecognized_query_parameter_is_rejected(self):
        response = self.client.get("/optimade/info?unknown=value")
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_unsupported_dimension_slices_returns_501(self):
        response = self.client.get(
            "/optimade/v1/structures?dimension_slices=dim_sites[0:1:1]"
        )
        self.assertEqual(response.status_code, 501)
        self.assertIn("errors", response.json())

    def test_legacy_unprefixed_oqmd_filter_is_rejected(self):
        response = self.client.get("/optimade/v1/structures?filter=stability=0")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown property", response.json()["errors"][0]["detail"])

    def test_structures_info_has_v1_2_property_definitions(self):
        response = self.client.get("/optimade/info/structures")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["id"], "structures")
        self.assertIn("space_group_it_number", data["properties"])
        self.assertEqual(
            data["properties"]["elements"]["$ref"],
            "https://schemas.optimade.org/defs/v1.2/properties/optimade/structures/elements",
        )


class OptimadeSerializerTestCase(SimpleTestCase):
    def test_structure_values_follow_optimade_types(self):
        site_al = SimpleNamespace(
            label="Al", atoms=[SimpleNamespace(cart_coord=np.array([0.0, 0.0, 0.0]))]
        )
        site_o = SimpleNamespace(
            label="O", atoms=[SimpleNamespace(cart_coord=np.array([1.0, 1.0, 1.0]))]
        )
        spacegroup = SimpleNamespace(number=221, hall="-P 4 2 3", hm="Pm-3m")
        structure = SimpleNamespace(
            x1=4.0,
            x2=0.0,
            x3=0.0,
            y1=0.0,
            y2=4.0,
            y3=0.0,
            z1=0.0,
            z2=0.0,
            z3=4.0,
            sites=[site_al, site_o],
            spacegroup=spacegroup,
            volume=64.0,
        )
        formation = SimpleNamespace(
            id=42,
            composition=SimpleNamespace(
                formula="Al2 O3",
                generic="A2B3",
                ntypes=2,
                element_list="Al_O_",
                unit_comp={"Al": 0.4, "O": 0.6},
            ),
            calculation=SimpleNamespace(id=7, output=structure, band_gap=1.2),
            entry=SimpleNamespace(
                id=9,
                natoms=2,
                keywords=[],
                path="",
                prototype=SimpleNamespace(name="AB2"),
            ),
            delta_e=-0.25,
            stability=0.0,
        )
        request = Request(APIRequestFactory().get("/optimade/v1/structures"))
        data = OptimadeStructureSerializer(
            formation, context={"request": request}
        ).data

        self.assertEqual(data["id"], "42")
        self.assertEqual(data["type"], "structures")
        self.assertEqual(data["elements"], ["Al", "O"])
        self.assertEqual(data["elements_ratios"], [0.4, 0.6])
        self.assertEqual(data["space_group_it_number"], 221)
        self.assertEqual(data["space_group_symbol_hall"], "-P 4 2 3")
        self.assertEqual(
            data["space_group_symbol_hermann_mauguin"], "Pm-3m"
        )
