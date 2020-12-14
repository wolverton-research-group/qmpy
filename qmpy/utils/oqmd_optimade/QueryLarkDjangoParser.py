import operator
import os
import re
from glob import glob
from lark import Lark, Tree, Token, Transformer
from django.db.models import Q
from qmpy.utils import parse_formula_regex
import qmpy
import json


class ParserError(Exception):
    def __init__(self,message):
        return('ParserError: {}'.format(message))

def get_grammar_data():
    parser_grammer = {}
    for name in glob(os.path.join(os.path.dirname(__file__), "./grammar", "*.g")):
        with open(name) as f:
            ver = tuple(
                int(n)
                for n in re.findall(r"\d+", str(os.path.basename(name).split(".g")[0]))
            )
            parser_grammer[ver] = Lark(f.read())
    return parser_grammer
        
        
class LarkParser:
    def __init__(self, version=None):
        parser_grammer = get_grammar_data()
        if version is None:
            self.version = sorted(parser_grammer.keys())[-1]
            self.lark = parser_grammer[self.version]
        elif version in parser_grammer:
            self.lark = parser_grammer[version]
            self.version = version
        else:
            raise ParserError("Unknown parser grammar version : " + str(version))
        self.tree = None
        self.filter = None

    def parse(self, filter_):
        try:
            self.tree = self.lark.parse(filter_)
            self.filter = filter_
            return self.tree
        except Exception as e:
            raise ParserError(e)

    def __repr__(self):
        if isinstance(self.tree, Tree):
            return self.tree.pretty()
        return repr(self.lark)

    
class Property:
    def __init__(self,
                 name,
                 db_value,
                 length_prop=None,
                 is_set_operable=False,
                 is_queryable=True,
                 is_logic_operable=True,
                 is_chem_form=False):            
        self.name = name
        self.db_value = db_value
        self.length_prop = length_prop
        self.is_set_operable = is_set_operable
        self.is_queryable = is_queryable
        self.is_chem_form = is_chem_form
        self.is_logic_operable = is_logic_operable

class Lark2Django(Transformer):
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
            "HAS_ALL" : self.has_all,
            "HAS_ANY" : self.has_any,
            "HAS_ONLY": self.has_only,
            "LENGTH"  : self.length_op_rhs
            
        }
        self.parser = LarkParser(version=(1, 0, 0))
        prop_data = json.load(
            open(
                sorted(
                    glob(os.path.join(os.path.dirname(__file__), "./grammar", "*.oqmd"))
                )[-1]
            )
        )
        self.property_dict = {}
        for item in prop_data:
            self.property_dict[item] = Property(**prop_data[item])
        
        self.logic_functions = [self.gt, self.ge, self.lt, self.le]
        self.elements = qmpy.elements.keys()

    def parse_raw_q(self, raw_query):
        return self.parser.parse(raw_query)
    
    def pretty_Q(self,qob,indent,ic):
        if isinstance(qob,Q):
            if qob.negated:
                qob.negated = False
                return ' '*indent*ic+'NOT\n'+self.pretty_Q(qob,indent,ic+1)
            connector_string = '\n'+' '*indent*ic+qob.connector+'\n'
            return connector_string.join([self.pretty_Q(item,indent,ic+1) for item in qob.children])
        elif isinstance(qob,tuple):
            return (' '*indent*(ic-1))+('='.join([str(item) for item in qob]))
        else:
            ParserError('Unsupported query or query children format found: {}'.format(type(qob)))
            
    def condensed_Q(self,qob):
        if isinstance(qob,Q):
            if qob.negated:
                qob.negated = False
                return '(NOT'+self.condensed_Q(qob)+')'
            connector_string = ' '+qob.connector+' '
            data_string = connector_string.join([self.condensed_Q(item) for item in qob.children])
            return '('+data_string+')'
        elif isinstance(qob,tuple):
            return ' '+('='.join([str(item) for item in qob]))+' '
        else:
            ParserError('Unsupported query or query children format found: {}'.format(type(qob)))
     
    def printable_djangoQ(self,qob,pretty=True,indent=4):
        if pretty:
            try:
                assert (indent>0 and type(indent)==int)
            except:
                raise ParserError('Indent value should be an integer >0 for pretty print')
            return self.pretty_Q(qob,indent,ic=0)
        else:
            return self.condensed_Q(qob)
            
    def eq(self, a, b):
        if isinstance(b,str):
            b = b.strip('"')
            if a.db_value == self.property_dict['element'].db_value:
                if not b.endswith('_'):
                    assert b in self.elements
                    b = b+'_'
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
        return ~q

    def and_(self, q1, q2):
        return operator.and_(q1, q2)

    def or_(self, q1, q2):
        return operator.or_(q1, q2)
    
    def has(self,a,b):
        return self.eq(a,b)
    
    def has_all(self,a,b):
        assert type(b)==list
        _q = self.has(a,b[0])
        b = b[1:]
        for i in range(len(b)):
            _q = self.and_(_q,self.has(a,b[i]))
        return _q
    
    def has_any(self,a,b):
        assert type(b)==list
        _q = self.has(a,b[0])
        b = b[1:]
        for i in range(len(b)):
            _q = self.or_(_q,self.has(a,b[i]))
        return _q
        
    def has_only(self,a,b):
        assert type(b)==list
        _q = self.has(a,b[0])
        b = b[1:]
        for i in range(len(b)):
            _q = self.and_(_q,self.has(a,b[i]))
        _q = self.and_(_q,self.length_eq(a,len(b)+1))
        return _q
    
    def length_eq(self,a,b):
        if a.length_prop:
            return self.eq(self.property_dict[a.length_prop],b)
        else:
            raise ParserError("Length does not exist for {}".format(a.name))
            
    def expression_clause(self,children):
        try:
            children = [item for item in children if not item==None]
            a = children[0]
            for b in children[1:]:
                a = self.and_(a,b)
            return a
        except:
            return None
        
    def expression_phrase(self,children):
        try:
            assert len(children)<3
            if len(children)==1:
                return children[0]
            else:
                assert children[0].type in self.opers
                return self.opers[children[0].type](children[1])
        except:
            return None
        
    def expression(self,children):
        try:
            children = [item for item in children if not item==None]
            a = children[0]
            for b in children[1:]:
                a = self.or_(a,b)
            return a
        except:
            return None
    
    def comparison(self,children):
        assert (len(children)==1)
        return children[0]
    
    def property_first_comparison(self,children):
        try:
            assert(len(children)==2 and children[0].data=='property')
            a = self._property(children[0])
            operation_fn = children[1][0]
            b = children[1][1]
            assert (a.is_queryable or a.db_value)
        
            if a.is_chem_form:
                c_dict_lst = parse_formula_regex(b)
                b = []
                for cd in c_dict_lst:
                    b.append(" ".join(["%s%g" % (k, cd[k]) for k in sorted(cd.keys())]))
                
            if operation_fn in self.logic_functions:
                assert a.is_logic_operable
            return operation_fn(a,b)
        except:
            return None
        
    def value_op_rhs(self,children):
        assert children[0].type=="OPERATOR"
        return [self.opers[children[0]], children[1]]
    
    def set_op_rhs(self,children):
        try:
            assert (children[0].type=="HAS" and len(children)<=3)
            if len(children)==2:
                return [self.opers[children[0].value],children[1]]
            else:
                set_operation_name = '_'.join([item.value for item in children[:2]])
                return [self.opers[set_operation_name],children[2]]
        except:
            return
        
    def length_op_rhs(self,children):
        assert len(children)==2
        return [self.opers[children[0].value],self.value(children[1])]
    
    def value_list(self,children):
        return list(children)
        
    def value(self,valTree):
        assert len(valTree[0].children)==1
        return valTree[0].children[0].value
    
    def _property(self,propTree):
        assert len(propTree.children)==1
        propToken = propTree.children[0]
        return self.property_dict[propToken.value]
    
    def filter(self,children):
        return children[0]
    
    def evaluate(self, tree):
        # For backward compatibility
        return self.transform(tree)
