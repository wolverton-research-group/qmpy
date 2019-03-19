from django.db.models import Q 
import operator
import qmpy.data as data

def precedence(op):
    if op == '-':
        return 2
    elif op == ',':
        return 1
    else:
        return 0

def applyOP(q1, q2, op):
    if op == '-':
        return reduce(operator.and_, [q1, q2])
    elif op == ',':
        return reduce(operator.or_, [q1, q2])

class Token:
    def __init__(self, tokens):
        self.tokens = tokens

    def element2q(self, val):
        if type(val) == Q:
            return val
        else:
            return Q(composition__element_list__contains=val+'_')

    def parse_element_group(self, group):
        lst = data.element_groups[group]
        q_lst = [Q(composition__element_list__contains=v+'_') for v in lst]
        return reduce(operator.or_, q_lst)

    def evaluate(self, method='element2q'):
        value_stack = []
        operator_stack = []

        tokens = self.tokens
        it = 0
        while it < len(tokens):
            t = tokens[it]

            if t == ' ':
                it += 1
                continue

            elif t.isupper():
                value_stack.append(t)
                it += 1
    
            elif t.islower():
                ele = value_stack.pop()
                ele += t
                value_stack.append(ele)
                it += 1
    
            elif t == '(':
                operator_stack.append(t)
                it += 1
    
            elif t == ')':
                while operator_stack[-1] != '(':
                    op = operator_stack.pop()
    
                    q2 = getattr(self, method)(value_stack.pop())
                    q1 = getattr(self, method)(value_stack.pop())
    
                    val = applyOP(q1, q2, op)
    
                    value_stack.append(val)
    
                operator_stack.pop()
                it += 1

            elif t == '{':
                it += 1
                t = tokens[it]
                group = ''
                while t != '}':
                    group += t
                    it += 1
                    t = tokens[it]
                it += 1
                value_stack.append(self.parse_element_group(group))
                continue
    
            elif t in ['-', ',']:
                thisop = t
                while operator_stack:
                    if not precedence(operator_stack[-1]) < precedence(thisop):
                        op = operator_stack.pop()
    
                        q2 = getattr(self, method)(value_stack.pop())
                        q1 = getattr(self, method)(value_stack.pop())
    
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

            q2 = getattr(self, method)(value_stack.pop())
            q1 = getattr(self, method)(value_stack.pop())
            
            val = applyOP(q1, q2, op)
            
            value_stack.append(val)
    
        return getattr(self, method)(value_stack.pop())
