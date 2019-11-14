import operator
import os
import re
from glob import glob
from lark import Lark, Tree, Token
from django.db.models import Q
from qmpy.utils import parse_formula_regex
import json


parser_grammer = {}
for name in glob(os.path.join(os.path.dirname(__file__), "./grammar", "*.g")):
    with open(name) as f:
        ver = tuple(
            int(n)
            for n in re.findall(r"\d+", str(os.path.basename(name).split(".g")[0]))
        )
        parser_grammer[ver] = Lark(f.read())


class ParserError(Exception):
    pass


class LarkParser:
    def __init__(self, version=None):
        if version is None:
            self.version = sorted(parser_grammer.keys())[-1]
            self.lark = parser_grammer[self.version]
        elif version in parser_grammer:
            self.lark = parser_grammer[version]
            self.version = version
        else:
            raise ParserError("Unknown parser grammar version : "+str(version))
        self.tree = None
        self.filter = None

    def parse(self, filter_):
        try:
            self.tree = self.lark.parse(filter_)
            self.filter = filter_
            return self.tree
        except Exception as e:
        #    print(e)
            return

    def __repr__(self):
        if isinstance(self.tree, Tree):
            return self.tree.pretty()
        else:
            return repr(self.lark)
        
        
        
class Lark2Django:
    def __init__(self):
        self.L2D_version = '0.1'
        self.opers = {'=':self.eq,  '>':self.gt,    '>=':self.ge, \
                      '<':self.lt,  '<=':self.le,   '!=':self.ne,\
                      'OR':self.or_,'AND':self.and_,'NOT':self.not_}
        self.parser = LarkParser(version=(0, 9, 7))
        self.db_keys = json.load(open(sorted(glob(os.path.join(os.path.dirname(__file__), "./grammar", "*.oqmd")))[-1]))
    def parse_raw_q(self,raw_query):
        return self.parser.parse(raw_query)
    
    def eq(self,a,b):
        return Q(**{a:b})
    
    def gt(self,a,b):
        return Q(**{a+'__gt':b})
    
    def ge(self,a,b):
        return Q(**{a+'__gte':b})
    
    def lt(self,a,b):
        return Q(**{a+'__lt':b})
    
    def le(self,a,b):
        return Q(**{a+'__lte':b})
    
    def ne(self,a,b):
        return ~Q(**{a:b})
    
    def not_(self,a):
        return ~a
    
    def and_(self,a,b):
        return operator.and_(a,b)
    
    def or_(self,a,b):
        return operator.or_(a,b)
    
    def evaluate(self,parse_Tree):
        if isinstance(parse_Tree,Tree):
            children = parse_Tree.children
            if len(children)==1:
                return self.evaluate(children[0])
            elif len(children)==2:
                op_fn = self.evaluate(children[0])
                return op_fn(self.evaluate(children[1]))
            elif len(children)==3:
                if parse_Tree.data=='comparison':
                    db_prop = self.evaluate(children[0])
                    op_fn = self.evaluate(children[1])

                    if db_prop=='element':
                        return op_fn(self.db_keys[db_prop],self.evaluate(children[2])+'_')

                    elif db_prop=='chemical_formula':
                        c_dict_lst = parse_formula_regex(self.evaluate(children[2]))
                        f_lst = []
                        for cd in c_dict_lst:
                            f = ' '.join(['%s%g' % (k,cd[k]) for k in sorted(cd.keys())])
                            f_lst.append(f)
                        return op_fn(self.db_keys[db_prop],f_lst)

                    else:
                        if db_prop in self.db_keys.keys():
                            _child_value = self.evaluate(children[2]).replace('"','')
                            return op_fn(self.db_keys[db_prop],_child_value)
                        else:
                            error_msg = "Unknown property is queried : "+(db_prop)
                            #print(error_msg)
                            return None
                        
                else:
                    op_fn = self.evaluate(children[1])
                    return op_fn(self.evaluate(children[0]),self.evaluate(children[2]))
            else:
                error_msg = "Not compatible format. Tree has >3 children"
                #print(error_msg)
                return(error_msg)
            
        elif isinstance(parse_Tree,Token):
            if parse_Tree.type == 'VALUE':
                return parse_Tree.value
            elif parse_Tree.type in ['NOT','CONJUNCTION','OPERATOR']:
                return self.opers[parse_Tree.value]
        else:
            error_msg = "Not a Lark Tree or Token. Check the parser implementation"
            #print(error_msg)
            return #(error_msg)
