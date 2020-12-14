// optimade v1.0.0 (also valid for v0.10.1) grammar spec in lark grammar format

?start: filter
filter: expression*

// Values
constant: string | number
// Note: support for property in value is OPTIONAL
value: string | number | property

// Note: not_implemented_string is only here to help Transformers
non_string_value: number | property
not_implemented_string: string

// Note:  support for OPERATOR in value_list is OPTIONAL
value_list: [ OPERATOR ] value ( "," [ OPERATOR ] value )*
// Note: support for OPERATOR in value_zip is OPTIONAL
value_zip: [ OPERATOR ] value ":" [ OPERATOR ] value (":" [ OPERATOR ] value)*
value_zip_list: value_zip ( "," value_zip )*

// Expressions
expression: expression_clause ( _OR expression_clause )*
expression_clause: expression_phrase ( _AND expression_phrase )*
expression_phrase: [ NOT ] ( comparison | "(" expression ")" )
// Note: support for constant_first_comparison is OPTIONAL
comparison: constant_first_comparison | property_first_comparison

// Note: support for set_zip_op_rhs in comparison is OPTIONAL
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
// Note: support for ONLY in set_op_rhs is OPTIONAL
// Note: support for [ OPERATOR ] in set_op_rhs is OPTIONAL
// set_op_rhs: HAS [ ALL | ANY | ONLY] value_list
set_op_rhs: HAS ( [ OPERATOR ] value
                 | ALL value_list
                 | ANY value_list
                 | ONLY value_list )

// Note: support for [ OPERATOR ] is OPTIONAL
length_op_rhs: LENGTH [ OPERATOR ] signed_int

set_zip_op_rhs: property_zip_addon HAS ( value_zip | ONLY value_zip_list | ALL value_zip_list | ANY value_zip_list )
property_zip_addon: ":" property (":" property)*

// Property syntax
property: IDENTIFIER ( "." IDENTIFIER )*

// String syntax
string: ESCAPED_STRING

// Number token syntax
number: SIGNED_INT | SIGNED_FLOAT

// Custom signed int
signed_int: SIGNED_INT

// Tokens

// Boolean relations
_AND:     "AND"
_OR:      "OR"
NOT:      "NOT"

IS:       "IS"
KNOWN:    "KNOWN"
UNKNOWN:  "UNKNOWN"

CONTAINS: "CONTAINS"
STARTS:   "STARTS"
ENDS:     "ENDS"
WITH:     "WITH"

LENGTH:   "LENGTH"
HAS:      "HAS"
ALL:      "ALL"
ONLY:     "ONLY"
ANY:      "ANY"

// Comparison OPERATORs
OPERATOR: ( "<" ["="] | ">" ["="] | ["!"] "=" )

IDENTIFIER: ( "_" | LCASE_LETTER ) ( "_" | LCASE_LETTER | DIGIT )*
LCASE_LETTER: "a".."z"
DIGIT: "0".."9"

// Strings

_STRING_INNER: /(.|[\t\f\r\n])*?/
_STRING_ESC_INNER: _STRING_INNER /(?<!\\)(\\\\)*?/

ESCAPED_STRING : "\"" _STRING_ESC_INNER "\""


%import common.SIGNED_INT
%import common.SIGNED_FLOAT

// White-space
%import common.WS
%ignore WS
