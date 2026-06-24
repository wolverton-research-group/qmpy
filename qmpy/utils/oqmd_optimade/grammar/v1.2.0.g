// OPTIMADE v1.2.0 filter grammar (used by the v1.3 specification)
// Adapted from https://github.com/Materials-Consortia/optimade-python-tools

?start: filter
filter: expression*

constant: string | number
value: string | bool | number | property
non_string_value: number | property
not_implemented_string: string

value_list: [ OPERATOR ] value ( "," [ OPERATOR ] value )*
value_zip: [ OPERATOR ] value ":" [ OPERATOR ] value (":" [ OPERATOR ] value)*
value_zip_list: value_zip ( "," value_zip )*

expression: expression_clause ( _OR expression_clause )*
expression_clause: expression_phrase ( _AND expression_phrase )*
expression_phrase: [ NOT ] ( comparison | "(" expression ")" )
comparison: constant_first_comparison | property_first_comparison

property_first_comparison: property ( value_op_rhs
                                    | known_op_rhs
                                    | fuzzy_string_op_rhs
                                    | set_op_rhs
                                    | set_zip_op_rhs
                                    | length_op_rhs )

constant_first_comparison: constant OPERATOR ( non_string_value | not_implemented_string )

value_op_rhs: OPERATOR value
known_op_rhs: IS ( KNOWN | UNKNOWN )
fuzzy_string_op_rhs: CONTAINS value
                   | STARTS [ WITH ] value
                   | ENDS [ WITH ] value
set_op_rhs: HAS ( [ OPERATOR ] value
                 | ALL value_list
                 | ANY value_list
                 | ONLY value_list )

length_op_rhs: LENGTH [ OPERATOR ] signed_int

set_zip_op_rhs: property_zip_addon HAS ( value_zip | ONLY value_zip_list | ALL value_zip_list | ANY value_zip_list )
property_zip_addon: ":" property (":" property)*

property: IDENTIFIER ( "." NESTED_IDENTIFIER )*
string: ESCAPED_STRING
bool: ( TRUE | FALSE )
number: SIGNED_INT | SIGNED_FLOAT
signed_int: SIGNED_INT

_AND:     "AND"
_OR:      "OR"
NOT:      "NOT"

IS:       "IS"
KNOWN:    "KNOWN"
UNKNOWN:  "UNKNOWN"
TRUE:     "TRUE"
FALSE:    "FALSE"

CONTAINS: "CONTAINS"
STARTS:   "STARTS"
ENDS:     "ENDS"
WITH:     "WITH"

LENGTH:   "LENGTH"
HAS:      "HAS"
ALL:      "ALL"
ONLY:     "ONLY"
ANY:      "ANY"

OPERATOR: ( "<" ["="] | ">" ["="] | ["!"] "=" )

IDENTIFIER: ( "_" | LCASE_LETTER ) ( "_" | LCASE_LETTER | DIGIT )*
NESTED_IDENTIFIER: ( "_" | LCASE_LETTER ) ( "_" | "+" | LCASE_LETTER | DIGIT )*
LCASE_LETTER: "a".."z"
DIGIT: "0".."9"

_STRING_INNER: /(.|[\t\f\r\n])*?/
_STRING_ESC_INNER: _STRING_INNER /(?<!\\)(\\\\)*?/

ESCAPED_STRING : "\"" _STRING_ESC_INNER "\""

%import common.SIGNED_INT
%import common.SIGNED_FLOAT
%import common.WS
%ignore WS
