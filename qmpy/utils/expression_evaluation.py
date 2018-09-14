from django.db.models import Q 
import operator

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

    def evaluate(self, method='element2q'):
        value_stack = []
        operator_stack = []

        tokens = self.tokens
        for t in tokens:
            if t.isupper():
                value_stack.append(t)
    
            elif t.islower():
                ele = value_stack.pop()
                ele += t
                value_stack.append(ele)
    
            elif t == '(':
                operator_stack.append(t)
    
            elif t == ')':
                while operator_stack[-1] != '(':
                    op = operator_stack.pop()
    
                    q2 = getattr(self, method)(value_stack.pop())
                    q1 = getattr(self, method)(value_stack.pop())
    
                    val = applyOP(q1, q2, op)
    
                    value_stack.append(val)
    
                operator_stack.pop()
    
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
    
            else:
                raise
    
        while operator_stack:
            op = operator_stack.pop()

            q2 = getattr(self, method)(value_stack.pop())
            q1 = getattr(self, method)(value_stack.pop())
            
            val = applyOP(q1, q2, op)
            
            value_stack.append(val)
    
        return value_stack.pop()
