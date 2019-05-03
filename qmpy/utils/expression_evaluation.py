from django.db.models import Q 
import operator
import re
import qmpy.data as data

def precedence(op):
    """ 
    Input:
        :str op: operator string
    Output:
        :int : priority of the operator
    """
    if op == '&':
        return 2
    elif op == '|':
        return 1
    else:
        return 0

def applyOP(q1, q2, op):
    """
    Function to apply operation
    Input:
        :Q q1: first django Q model
        :Q q2: seconde django Q model
        :str op: operator, '&' or '|' 
    Output:
        :Q : reduced django Q model
    """
    if op == '&':
        return reduce(operator.and_, [q1, q2])
    elif op == '|':
        return reduce(operator.or_, [q1, q2])

def element_set_conversion(filter_expr):
    """
    Convert element_set filter to multiple element filters
    Input:
        :str filter_expr: raw filter expression w/ element_set parameter
            Valid element_set expression:
                ',': AND operator
                ';': OR operator
                '(', ')': to change precedence
            Examples:
                element_set=Al;O,H
                element_set=(Mn;Fe),O
    Output:
        :str : converted filter expression
    """
    filter_expr_out = filter_expr

    for els in re.findall('element_set=[\S]*', filter_expr):
        els_out = els.replace('element_set=', '')

        for el in re.findall('[A-Z][a-z]*', els):
            els_out = els_out.replace(el, ' element='+el+' ')

        els_out = els_out.replace(',', '&')
        els_out = els_out.replace(';', '|')

        filter_expr_out = filter_expr.replace(els, '('+els_out+')')

    return filter_expr_out

class Token(object):
    def __init__(self, tokens):
        # preprocess token if 'element_set' included
        if 'element_set' in tokens:
            tokens = element_set_conversion(tokens)

        self.tokens = tokens
        

    def filter_formationenergy(self, expr):
        """
        Function to convert expression into Q model
        Input: 
            :str expr: format should be 'attribute=value' e.g. 'element=Fe'
                list of valid attributes:
                    element, generic, prototype, spacegroup,
                    volume, natoms, ntypes, stability,
                    delta_e, band_gap
                Space padding is required between expression. For each epression,
                space is not allowed.
                    Valid examples:
                        'element=Mn & band_gap>1'
                        '( element=O | element=S ) & natoms<3'
                    Invalid examples:
                        'element = Fe'
                        '( element=Fe & element=O)'
        Output:
            :Q : django Q model
        """
        if type(expr) == Q:
            return expr
        else:
            attr = re.split("[=<>]", expr)[0]
            val = re.split("[=<>]", expr)[1]

            if attr == "element":
                return Q(composition__element_list__contains=val+'_')

            elif attr == "generic":
                return Q(composition__generic=val)

            elif attr == "prototype":
                return Q(entry__prototype=val)

            elif attr == "spacegroup":
                return Q(calculation__output__spacegroup__hm=val)

            elif attr == "volume":
                if '>' in expr:
                    return Q(calculation__output__volume__gt=val)
                elif '<' in expr:
                    return Q(calculation__output__volume__lt=val)
                elif '=' in expr:
                    return Q(calculation__output__volume=val)

            elif attr == "natoms":
                if '>' in expr:
                    return Q(entry__natoms__gt=val)
                elif '<' in expr:
                    return Q(entry__natoms__lt=val)
                elif '=' in expr:
                    return Q(entry__natoms=val)

            elif attr == "ntypes":
                if '>' in expr:
                    return Q(entry__ntypes__gt=val)
                elif '<' in expr:
                    return Q(entry__ntypes__lt=val)
                elif '=' in expr:
                    return Q(entry__ntypes=val)

            elif attr == "stability":
                if '>' in expr:
                    return Q(stability__gt=val)
                elif '<' in expr:
                    return Q(stability__lt=val)
                elif '=' in expr:
                    return Q(stability=val)

            elif attr == "delta_e":
                if '>' in expr:
                    return Q(delta_e__gt=val)
                elif '<' in expr:
                    return Q(delta_e__lt=val)
                elif '=' in expr:
                    return Q(delta_e=val)

            elif attr == "band_gap":
                if '>' in expr:
                    return Q(calculation__band_gap__gt=val)
                elif '<' in expr:
                    return Q(calculation__band_gap__lt=val)
                elif '=' in expr:
                    return Q(calculation__band_gap=val)

            return Q()

#    def parse_element_group(self, group):
#        lst = data.element_groups[group]
#        q_lst = [Q(composition__element_list__contains=v+'_') for v in lst]
#        return reduce(operator.or_, q_lst)

    def evaluate_filter(self, origin='formationenergy'):
        """
        Evaluate the token and parse it to django Q operation
        Input:
            :str origin: formationenergy, etc
        Output:
            :Q : django Q model
        """
        value_stack = []
        operator_stack = []

        tokens = self.tokens
        it = 0
        while it < len(tokens):
            t = tokens[it]

            if t == ' ':
                it += 1
                continue

            elif t.isalpha():
                expr = ''
                while t != ' ' and it < len(tokens):
                    expr += t
                    it += 1
                    if it < len(tokens):
                        t = tokens[it]
                value_stack.append(expr)
    
            elif t == '(':
                operator_stack.append(t)
                it += 1
    
            elif t == ')':
                while operator_stack[-1] != '(':
                    op = operator_stack.pop()
    
                    q2 = getattr(self, 'filter_'+origin)(value_stack.pop())
                    q1 = getattr(self, 'filter_'+origin)(value_stack.pop())
    
                    val = applyOP(q1, q2, op)
    
                    value_stack.append(val)
    
                operator_stack.pop()
                it += 1

            elif t in ['&', '|']:
                thisop = t
                while operator_stack:
                    if not precedence(operator_stack[-1]) < precedence(thisop):
                        op = operator_stack.pop()
    
                        q2 = getattr(self, 'filter_'+origin)(value_stack.pop())
                        q1 = getattr(self, 'filter_'+origin)(value_stack.pop())
    
                        val = applyOP(q1, q2, op)
    
                        value_stack.append(val)
                    else:
                        break
    
                operator_stack.append(thisop)
                it += 1
    
            else:
                raise
    
        while operator_stack:
            op = operator_stack.pop()

            q2 = getattr(self, 'filter_'+origin)(value_stack.pop())
            q1 = getattr(self, 'filter_'+origin)(value_stack.pop())
            
            val = applyOP(q1, q2, op)
            
            value_stack.append(val)
    
        return getattr(self, 'filter_'+origin)(value_stack.pop())
