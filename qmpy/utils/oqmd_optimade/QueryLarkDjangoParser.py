import operator
import os
import re
from glob import glob
from lark import Lark, Tree, Token, Transformer
from django.db.models import Q
from qmpy.utils import parse_formula_regex
import qmpy
import json
from rest_framework.exceptions import ParseError, APIException
from lark.exceptions import VisitError
from copy import deepcopy


class LarkParserError(Exception):
    pass


def get_grammar_data():
    parser_grammer = {}
    for name in glob(os.path.join(os.path.dirname(__file__), "grammar", "*.g")):
        with open(name) as f:
            ver = tuple(
                int(n)
                for n in re.findall(r"\d+", os.path.splitext(os.path.basename(name))[0])
            )
            parser_grammer[ver] = Lark(f.read())
    return parser_grammer


class LarkParser(object):
    """
    Parser to convert a given filter string to a Tree-Token system according to
    the grammar rules provided
    The grammar files are identified with an extension `.g`
    """

    def __init__(self, version=None):
        """
        Constructor Function which optionally accepts the grammar version number
        while creating a Lark object
        If no version is provided, the grammar file with highest version number
        is used for parsing

        """
        parser_grammer = get_grammar_data()
        if version is None:
            self.version = sorted(parser_grammer.keys())[-1]
            self.lark = parser_grammer[self.version]
        elif version in parser_grammer:
            self.lark = parser_grammer[version]
            self.version = version
        else:
            raise LarkParserError("Unknown parser grammar version : " + str(version))
        self.tree = None
        self.filter = None

    def parse(self, filter_):
        """
        Function which parses a given filter
        Examples::
            >>> if LarkParser().parse("nsites>1"): print("Success")
                Success
            >>> tree = LarkParser().parse('chemical_formula_reduced=Al2O3').pretty()
                ParseError: Error while parsing the filter with optimade grammar version :(1, 0, 0)
        """

        try:
            self.tree = self.lark.parse(filter_)
            self.filter = filter_
            return self.tree
        except Exception as e:
            error_message = (
                "Error while parsing the filter with optimade grammar version: "
            )
            error_message += "v{}. ".format(
                ".".join([str(item) for item in self.version])
            )
            error_message += "Check for grammatical errors in the query"
            raise ParseError(error_message)

    def __repr__(self):
        if isinstance(self.tree, Tree):
            return self.tree.pretty()
        return repr(self.lark)


class RESTProperty(object):
    """
    Represents a queryable or non-queryable property in RESTful request's filters or fields
    """

    def __init__(
        self,
        name,
        db_value,
        length_prop=None,
        is_set_operable=False,
        is_queryable=True,
        is_logic_operable=True,
        is_chem_form=False,
    ):
        self.name = name
        self.db_value = db_value
        self.length_prop = length_prop
        self.is_set_operable = is_set_operable
        self.is_queryable = is_queryable
        self.is_chem_form = is_chem_form
        self.is_logic_operable = is_logic_operable


class Lark2Django(Transformer):
    """
    Custom Transformer inherited from lark.Transformer to convert parsed Lark trees to Django Queries

    Attributes
    parser : LarkParser object initialized with the latest version of grammar
    property_dict : Dictionary of Property objects identified by their filter-key names
    warnings : List of warnings generated during the transform. Used perdominantly to
               warn the client about omissions of property comparisons from the original query
    error_types : Types of errors available for this Transformer
    opers : Dict of comparison operators identified by their label in REST specification
    """

    def __init__(self):
        self.L2D_version = "1.0"
        self.opers = {
            "=": self.eq,
            ">": self.gt,
            ">=": self.ge,
            "<": self.lt,
            "<=": self.le,
            "!=": self.ne,
            "OR": self.or_,
            "AND": self.and_,
            "NOT": self.not_,
            "HAS": self.has,
            "HAS_ALL": self.has_all,
            "HAS_ANY": self.has_any,
            "HAS_ONLY": self.has_only,
            "LENGTH": self.length_eq,
            "STARTS": self.starts,
            "ENDS": self.ends,
            "CONTAINS": self.contains
        }
        self.fuzzy_functions_list = {
                self.starts,
                self.ends,
                self.contains
                }
        self.parser = LarkParser(version=(1, 0, 0))
        prop_data = json.load(
            open(
                sorted(
                    glob(os.path.join(os.path.dirname(__file__), "grammar", "*.oqmd"))
                )[-1]
            )
        )
        self.property_dict = {}
        for item in prop_data:
            self.property_dict[item] = RESTProperty(**prop_data[item])

        self.logic_functions = [self.gt, self.ge, self.lt, self.le]
        self.elements = qmpy.elements.keys()
        self.warnings = []
        self.error_types = {
            "T1": "IgnoredProperty",
            "T2": "InvalidLabel",
            "T3": "NotSupported",
            "T4": "GeneralWarning",
        }

    def handle_error(self, error_type, message, object_label="", raise_error=True):
        """
        Add warning/error message to the class attribute warnings

        Parameters:
            error_type : Warning types are defined in class attribute `warn_types`
            message   : Custom message describing the reason why the warning was generated
            object_label : label of the property/operator/values which is affiliated with the warning
        """
        if error_type in self.error_types:
            warn_message = self.error_types[error_type]
        else:
            warn_message = "UnknownError"
        warn_message = "_oqmd_" + warn_message
        warn_message = " :: ".join([warn_message, str(object_label), message])
        if str(object_label).startswith("_"):
            raise_error = False

        if not raise_error:
            self.warnings.append(warn_message)
        else:
            raise ParseError(warn_message)

    def parse_raw_q(self, raw_query):
        """
        Parse the raw filter query from client requent to a Tree-Token system using Lark

        Parameters:
            raw_query : Raw filter query (Ex: 'nsites>1 OR band_gap=3 AND delta_e<0')
        Returns :
            A Lark Tree object
        """
        return self.parser.parse(raw_query)

    def pretty_Q(self, qob, indent, ic):
        """
        Pretty print Django query
        """
        if isinstance(qob, Q):
            if qob.negated:
                qob.negated = False
                return " " * indent * ic + "NOT\n" + self.pretty_Q(qob, indent, ic + 1)
            connector_string = "\n" + " " * indent * ic + qob.connector + "\n"
            return connector_string.join(
                [self.pretty_Q(item, indent, ic + 1) for item in qob.children]
            )
        elif isinstance(qob, tuple):
            return (" " * indent * (ic - 1)) + ("=".join([str(item) for item in qob]))
        else:
            LarkParserError(
                "Unsupported query or query children format found: {}".format(type(qob))
            )

    def condensed_Q(self, qob):
        """
        Print Django query without indentation and newlines
        """

        if isinstance(qob, Q):
            if qob.negated:
                qob.negated = False
                return "(NOT" + self.condensed_Q(qob) + ")"
            connector_string = " " + qob.connector + " "
            data_string = connector_string.join(
                [self.condensed_Q(item) for item in qob.children]
            )
            return "(" + data_string + ")"
        elif isinstance(qob, tuple):
            return " " + ("=".join([str(item) for item in qob])) + " "
        else:
            LarkParserError(
                "Unsupported query or query children format found: {}".format(type(qob))
            )

    def printable_djangoQ(self, _qob, pretty=True, indent=4):
        """
        Print Django query in a readable format
        """
        qob = deepcopy(_qob)
        if qob is None:
            return
        if pretty:
            try:
                assert indent > 0 and isinstance(indent, int)
            except:
                raise LarkParserError(
                    "Indent value should be an integer >0 for pretty print"
                )
            return self.pretty_Q(qob, indent, ic=0)
        else:
            return self.condensed_Q(qob)

    def eq(self, a, b):
        if isinstance(b, str):
            b = b.strip('"')
            if a.db_value == self.property_dict["element"].db_value:
                if not b.endswith("_"):
                    if not b in self.elements:
                        raise ParseError("Unknown element name queried: {}".format(b))
                    b = b + "_"
        return Q(**{a.db_value: b})

    def gt(self, a, b):
        return Q(**{a.db_value + "__gt": b})

    def ge(self, a, b):
        return Q(**{a.db_value + "__gte": b})

    def lt(self, a, b):
        return Q(**{a.db_value + "__lt": b})

    def le(self, a, b):
        return Q(**{a.db_value + "__lte": b})

    def ne(self, a, b):
        return ~Q(**{a.db_value: b})

    def not_(self, q):
        if q is None:
            return
        return ~q

    def and_(self, q1, q2):
        return operator.and_(q1, q2)

    def or_(self, q1, q2):
        return operator.or_(q1, q2)

    def has(self, a, b):
        """
        HAS operator is introduced by optimade specs to query within a list-type property

        This operator is applicable only on list-type Property objects identified by their
        Property.is_set_operable attribute

        Example:
               elements HAS "Al"  : will add a filter to include only those structures whose
                                    `elements` property contains the element "Al"
        """
        if not a.is_set_operable:
            self.handle_error("T3", "Not supported for {}".format(a.name), "HAS")
        return self.eq(a, b)

    def has_all(self, a, b):
        """
        Similar to HAS, but oeprable on multiple values with AND connector

        Example:
            elements HAS ALL "Al","Fe","O" : will add a filter to only those structures
                                             whose `elements` property contains all the
                                             elements specified - Al, Fe and O

            property HAS ALL "A","B"  :is converted into  (property HAS "A" AND property HAS "B")
        """
        if a.is_set_operable:
            _q = self.has(a, b[0])
            b = b[1:]
            for i in range(len(b)):
                _q = self.and_(_q, self.has(a, b[i]))
            return _q
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "HAS ALL")

    def has_any(self, a, b):
        """
        Similar to HAS, but oeprable on multiple values with an OR connector

        Example:
            elements HAS ANY "Al","Fe","O" : will add a filter to only those structures
                                             whose `elements` property contains at least
                                             one of elements specified - Al, Fe or O

            property HAS ANY "A","B"  :is converted into  (property HAS "A" ANY property HAS "B")
        """
        if a.is_set_operable:
            _q = self.has(a, b[0])
            b = b[1:]
            for i in range(len(b)):
                _q = self.or_(_q, self.has(a, b[i]))
            return _q
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "HAS ANY")

    def has_only(self, a, b):
        """
        Similar to HAS, but oeprable on multiple values with AND connector and limiting
        constraint on the property's data

        Example:
            elements HAS ONLY "Al","Fe","O" : will add a filter to only those structures
                                             whose `elements` property contains exactly the
                                             elements specified - Al, Fe and O

            property HAS ONLY "A","B"  : is converted into, assuming length of property is
                                         described by a nproperty
                                        (property HAS "A" AND property HAS "B" AND nproperty=2)

            Length of the property `elements` is described by the property `nelements` in optiamde
            Length of the property `elements` is described by the property `ntypes` in oqmdapi
            Length of the property `sites` is described by the property `nsites` in optimade
            Length of the property `sites` is described by the property `natoms` in oqmdapi
        """

        if a.is_set_operable and a.length_prop:
            _q = self.has(a, b[0])
            b = b[1:]
            for i in range(len(b)):
                _q = self.and_(_q, self.has(a, b[i]))
            return self.and_(_q, self.length_eq(a, len(b) + 1))
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "HAS ONLY")

    def starts(self,a,b):
        if a.is_chem_form:
            _db_value = a.db_value.strip("__in")
            _db_value = _db_value + "__startswith"
            return Q(**{_db_value: b})
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "STARTS")
            
    def ends(self,a,b):
        if a.is_chem_form:
            _db_value = a.db_value.strip("__in")
            _db_value = _db_value + "__endswith"
            return Q(**{_db_value: b})
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "ENDS")
            
    def contains(self,a,b):
        if a.is_chem_form:
            _db_value = a.db_value.strip("__in")
            _db_value = _db_value + "__contains"
            return Q(**{_db_value: b})
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "CONTAINS")


    def length_eq(self, a, b):
        """
        A set operation to constrain length of a property to a given integer

        Example:
            elements LENGTH 3 : is converted to `nelements=3`

            Length of the property `elements` is described by the property `nelements` in optiamde
            Length of the property `elements` is described by the property `ntypes` in oqmdapi
            Length of the property `sites` is described by the property `nsites` in optimade
            Length of the property `sites` is described by the property `natoms` in oqmdapi
        """

        if a.length_prop:
            return self.eq(self.property_dict[a.length_prop], b)
        else:
            self.handle_error("T3", "Not supported for {}".format(a.name), "LENGTH")

    def expression_clause(self, children):
        if children is None:
            return
        children = [item for item in children if item is not None]
        if len(children) > 0:
            a = children[0]
            for b in children[1:]:
                a = self.and_(a, b)
            return a

    def expression_phrase(self, children):
        if children is None:
            return
        elif len(children) == 1:
            return children[0]
        elif children[0].value in self.opers:
            return self.opers[children[0].value](children[1])
        else:
            self.handle_error("T2", "Label not found", children[0].value)

    def expression(self, children):
        children = [item for item in children if item is not None]
        if len(children) > 0:
            a = children[0]
            for b in children[1:]:
                a = self.or_(a, b)
            return a

    def comparison(self, children):
        return children[0]

    def property_first_comparison(self, children):
        """
        This function is automatically called by the Transformer when it encounters a Tree
        with Tree.data = property_first_comparison

        As of now, all the supported value comparisons in OQMD's optimade implementation are
        property-first comparisons. Because of that, this function is called by each filter
        element

        Format of property-first comparison: "property operator value(s)"

        Example:
            stability < 0.05   :  Here, `stability` is the property, `<` is the operator,
                                  and `0.05` is the value
        """
        _property = children[0].children[0].value
        try:
            a = self.property_dict[_property]
        except:
            self.handle_error("T1", "Cannot resolve the property name", _property)
            return

        if children[1] is None:
            self.handle_error(
                "T1", "Accompanying Operator or Value cannot be parsed", a.name
            )
            return

        operation_fn = children[1][0]
        b = children[1][1]

        if not (a.is_queryable and a.db_value):
            if (a.name == "nperiodic_dimensions"):
                if (operation_fn == self.eq and int(b)==3) or (operation_fn == self.ne and int(b)!=3):
                    return self.gt(self.property_dict['volume'],0)
                else:
                    error_message = "All structures  in OQMD have nperiodic_dimensions=3"
                    self.handle_error("T4",error_message, a.name, raise_error=False)
                    return self.eq(self.property_dict['volume'],0)
            elif (a.name == "structure_features"):
                error_message = "No structure_features are included in OQMD"
                error_message = error_message + "A dummy query (id=-1) to return none is executed"
                self.handle_error("T4",error_message, a.name, raise_error=False)
                return self.eq(self.property_dict['id'],-1)
            self.handle_error("T1", "Cannot be queried in filter", a.name)
            return

        if a.is_chem_form:
            b=b.strip('"')
            if not (len(b)==0 or operation_fn in self.fuzzy_functions_list):
                b=b.strip('"')
                c_dict_lst = parse_formula_regex(b)
                if len(c_dict_lst) == 1 and len(c_dict_lst[0].keys()) == 0:
                    self.handle_error(
                        "T1", "Chemical formula {} cannot be parsed".format(b), a.name
                    )
                    return
                b = [
                    " ".join(["%s%g" % (k, cd[k]) for k in sorted(cd.keys())])
                    for cd in c_dict_lst
                ]

        if operation_fn in self.logic_functions:
            if not a.is_logic_operable:
                self.handle_error(
                    "T1", "Cannot be queried with operators <,>,<=,>=", a.name
                )
                return
        try:
            return operation_fn(a, b)
        except ParseError as err:
            raise err
        except:
            self.handle_error(
                "T1", "Unknown error while converting to Django Q", a.name
            )

    def constant_first_comparison(self, children):
        self.handle_error("T3", "Not supported yet", "CONSTANT FIRST COMPARISON")

    def known_op_rhs(self, children):
        self.handle_error("T3", "Not supported yet", "KNOWN OPERATION")

    def fuzzy_string_op_rhs(self, children):
        if children[0] in self.opers:
            return [self.opers[children[0].value],children[-1]]
        self.handle_error("T3", "Not supported yet", "FUZZY STRING OPERATIONS")

    def value_op_rhs(self, children):
        if children[0] in self.opers:
            return [self.opers[children[0]], children[1]]
        else:
            self.handle_error("T2", "Label not found", children[0])

    def set_op_rhs(self, children):
        if len(children) == 2:
            set_operation_name = children[0].value
        else:
            set_operation_name = "_".join([item.value for item in children[:2]])

        if children[0] in self.opers:
            return [self.opers[set_operation_name], children[-1]]
        else:
            self.handle_error("T2", "Label not found", set_operation_name)

    def length_op_rhs(self, children):
        if len(children) > 2:
            self.handle_error(
                "T3",
                "Not supported with >,<,=,etc. (Allowed format: property LENGTH value)",
                "LENGTH",
            )
        if children[0].value in self.opers:
            return [self.opers[children[0].value], self.value([children[1]])]
        else:
            self.handle_error("T2", "Label not found", children[0].value)

    def value_list(self, children):
        """
        A list of values are provided for set operations
        """
        return list(children)

    def value(self, val_tree):
        return val_tree[0].children[0].value

    def filter(self, children):
        return children[0]

    def evaluate(self, tree):
        """
        Evaluate a given Lark tree and return corresponding Django Query and meta data

        Parameters:
                  tree : A Lark Tree object
        Returns:
                  1. Django Q object generated by transforming the input tree
                  2. Meta data with warnings and a readable representation of
                     of the final Django query that's being returned. More data
                     may be added in later when the API specifications change
        """
        error_message_500 = (
            "Your query could not be transformed to a Django query filter ."
        )
        error_message_500 += "Let us know if your query filter is in accoradnce with OQMD's current optimade version"
        try:
            django_q = self.transform(tree)
        except ParseError as err:
            raise err
        except VisitError as err:
            if isinstance(err.orig_exc, ParseError):
                raise ParseError(err.orig_exc)
            else:
                raise APIException(error_message_500, code=500)
        except:
            raise APIException(error_message_500, code=500)

        self.warnings = [ 
                { "type":"warning", "detail":warn_message} for warn_message in list(set(self.warnings))
                ]
        meta_info = {
            "warnings": self.warnings,
            "django_query": self.printable_djangoQ(django_q, pretty=False),
        }
        return (django_q, meta_info)
