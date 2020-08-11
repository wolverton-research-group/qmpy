// optimade v0.9.5 grammar spec in lark grammar format

start: KEYWORD expression
KEYWORD: "filter="
expression: [expression OR] term
term: [term AND] atom
atom: [NOT] comparison
    | [NOT] "(" (andcomparison OR)* andcomparison ")"
andcomparison: [NOT] (NOT comparison AND)* comparison
comparison: VALUE OPERATOR VALUE
OPERATOR: /<=?|>=?|!?=/
VALUE: CNAME | SIGNED_FLOAT | SIGNED_INT | ESCAPED_STRING
AND: /and/i
OR: /or/i
NOT: /not/i
%import common.CNAME
%import common.SIGNED_FLOAT
%import common.SIGNED_INT
%import common.ESCAPED_STRING
%import common.WS_INLINE
%ignore WS_INLINE
