from qmpy.utils import *
from django.test import TestCase
from django.db.models import Q
from rest_framework.exceptions import ParseError


class RESTfulTestCase(TestCase):
    def setUp(self):
        self.transformer = Lark2Django()

    def transform_q(self,query,return_mode=0):
        """
        Three return modes are available as of now
        
        return_mode=0 : Returns the default string representation of final Django query
        return_mode=1 : Returns the warnings-list from the parser
        return_mode=2 : Returns the custom string representation of final Django query
        return_mode=3 : Returns the exception received from transformer
        """
        self.transformer = Lark2Django()
        tree = self.transformer.parse_raw_q(query)
        if return_mode==0:
            return self.transformer.evaluate(tree)[0].__str__()
        elif return_mode==1:
            return self.transformer.evaluate(tree)[1]['warnings']
        elif return_mode==2:
            return self.transformer.evaluate(tree)[1]['django_query']
        elif return_mode==3:
            _0,_1 = self.transformer.evaluate(tree)


    def test_djangoQ_printer(self):
        truth_value = '(((NOT( stability__gt=0 )) AND ( calculation__band_gap__gt=2  OR  composition__element_list__contains=Fe_  OR  composition__element_list__contains=Mn_ )) OR ( calculation__band_gap__gt=2  AND ((NOT( composition__generic=AB )) OR  calculation__output__spacegroup__hm=Fm-3m )))'
        assert truth_value == self.transform_q('NOT stability>0 AND (_oqmd_band_gap>2 OR elements HAS ANY "Fe","Mn") OR (_oqmd_band_gap>2 AND (NOT generic="AB" OR _oqmd_spacegroup="Fm-3m"))',2)
        
    def test_queries(self):

        # Testing numerical value parsing
        truth_value = "(OR: (AND: ('stability', '0'), ('calculation__band_gap__gt', '0.5')), ('calculation__output__volume__gt', '1.4e+2'))"
        assert truth_value == self.transform_q('stability=0     AND band_gap>0.5 OR volume>1.4e+2',0)
        assert truth_value == self.transform_q('stability=0ANDband_gap>0.5ORvolume>1.4e+2',0)
        assert truth_value == self.transform_q('stability=0 AND band_gap>0.5 OR volume>1.4e+2',0)

        # Testing old OQMD property names with new optimade names
        truth_value = "(OR: ('entry__composition__ntypes__lte', '3'), ('entry__composition__ntypes__gt', '5'))"
        assert truth_value == self.transform_q('nelements<=3 OR ntypes>5')
        truth_value = "(OR: ('stability__lte', '-0.2'), ('stability__gt', '1.'))"
        assert truth_value == self.transform_q('stability<=-0.2 OR _oqmd_stability>1.')
        truth_value = "(OR: ('entry__composition__ntypes', '3'), ('entry__composition__ntypes', '5'))"
        assert truth_value == self.transform_q('elements LENGTH 3 OR nelements=5')

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
        assert truth_value == self.transform_q('elements LENGTH 3')


        # queries that return 'None'. i.e; no data is returned but a BadRequest400 error is not raised
        truth_value = 'None'
        assert truth_value == self.transform_q('_abc_elements LENGTH 3')

        # Other property-dependant tests
        truth_value = "(AND: ('id', '1234'))"
        assert truth_value == self.transform_q('id="1234"')
        truth_value = "(AND: ('composition__formula__in', ['Al2 O3']))"
        assert truth_value == self.transform_q('chemical_formula_reduced="Al2O3"')
        truth_value = "(AND: ('composition__formula__in', ['Co1 O3', 'Cr1 O3', 'Cu1 O3', 'Fe1 O3', 'Mn1 O3', 'Ni1 O3', 'O3 Sc1', 'O3 Ti1', 'O3 V1', 'O3 Zn1']))"
        assert truth_value == self.transform_q('chemical_formula_reduced="{3d}O3"')
        

        # Miscellaneous Tests
        truth_value = "(NOT (AND: ('stability__gt', '3')))"
        assert truth_value == self.transform_q('NOT stability > 3')
        truth_value = "(OR: (AND: (NOT (AND: ('stability__gt', '0'))), (OR: ('calculation__band_gap__gt', '2'), ('composition__element_list__contains', 'Fe_'), ('composition__element_list__contains', 'Mn_'))), (AND: ('calculation__band_gap__gt', '2'), (OR: (NOT (AND: ('composition__generic', 'AB'))), ('calculation__output__spacegroup__hm', 'Fm-3m'))))"
        assert truth_value == self.transform_q('NOT stability>0 AND (_oqmd_band_gap>2 OR elements HAS ANY "Fe","Mn") OR (_oqmd_band_gap>2 AND (NOT generic="AB" OR _oqmd_spacegroup="Fm-3m"))')
        truth_value = "(AND: ('composition__formula__in', ['Al1']))"
        assert truth_value == self.transform_q('chemical_formula_reduced= "   Al "')
        truth_value = "(AND: ('entry__natoms__lt', '8'))"
        assert truth_value == self.transform_q('nsites<8 AND _<0')
        truth_value = "(AND: ('entry__natoms__lt', '8'))"
        assert truth_value == self.transform_q('nsites<8 AND _abc_stability<0')
        truth_value = "(AND: ('id', '112/23344'))"
        assert truth_value == self.transform_q('id="112/23344"')


    def test_errors(self):
        self.assertRaises(ParseError, self.transform_q,'abc_elements LENGTH 3', 3)
        self.assertRaises(ParseError, self.transform_q,'xyz = 3', 3)
        self.assertRaises(ParseError, self.transform_q, 'abcd=0 AND band_gap>0 OR lattice_vectors=12345', 3)
        self.assertRaises(ParseError, self.transform_q, 'stability>0 OR NOT lattice_vectors>12345', 3)
        self.assertRaises(ParseError, self.transform_q, 'band_gap>0 OR NOT id>12345', 3)
        self.assertRaises(ParseError, self.transform_q, 'elements HAS "A"', 3)
        self.assertRaises(ParseError, self.transform_q, 'elements HAS ANY "Al",D', 3)
        self.assertRaises(ParseError, self.transform_q, 'elements HAS Al', 3)
        self.assertRaises(ParseError, self.transform_q, 'id=112/23344', 3)
        self.assertRaises(ParseError, self.transform_q, 'elements LENGTH > 3', 3)
        self.assertRaises(ParseError, self.transform_q, 'stability HAS 1', 3)
        self.assertRaises(ParseError, self.transform_q, 'id>"1234"', 3)
        self.assertRaises(ParseError, self.transform_q, 'OR stability > 3', 3)
        self.assertRaises(ParseError, self.transform_q, 'NOT abcd > 3', 3)
        self.assertRaises(ParseError, self.transform_q, 'AND', 3)
        self.assertRaises(ParseError, self.transform_q, 'chemical_formula_reduced=Al2O3', 3)
        self.assertRaises(ParseError, self.transform_q, 'chemical_formula_reduced="{4z}"', 3)
        self.assertRaises(ParseError, self.transform_q, 'elements HAS "   Al "', 3)
        self.assertRaises(ParseError, self.transform_q, ' < 0', 3)
        self.assertRaises(ParseError, self.transform_q, 'AND < 0', 3)
        self.assertRaises(ParseError, self.transform_q, ' < 0', 3)
        self.assertRaises(ParseError, self.transform_q, ' < 0', 3)

        # Following tests should be modified when OQMD start supporting these kinda queries
        self.assertRaises(ParseError, self.transform_q, '3 > stability', 3)
        self.assertRaises(ParseError, self.transform_q, 'stability IS KNOWN', 3)
        self.assertRaises(ParseError, self.transform_q, 'chemical_formula_reduced CONTAINS "Al"', 3)

    def test_warnings(self):
        assert self.transform_q('_abc_stability < 0', 1)[0].startswith('_oqmd_IgnoredProperty')
        assert self.transform_q('_ >= 0', 1)[0].startswith('_oqmd_IgnoredProperty')
        assert self.transform_q('nsites<8 AND _<0', 1)[0].startswith('_oqmd_IgnoredProperty')
        assert self.transform_q('nsites<8 AND nelements<4', 1) == []

