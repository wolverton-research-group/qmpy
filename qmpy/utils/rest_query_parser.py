import re
from oqmd_optimade import Lark2Django

def element_set_conversion(filter_expr):
    """
    Convert element_set filter to multiple element filters
    Input:
        :str filter_expr: raw filter expression w/ element_set parameter
            Valid element_set expression:
                ',': AND operator
                '-': OR operator
                '~': NOT operator
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

        els_out = els_out.replace(',', ' AND ')
        els_out = els_out.replace('-', ' OR ')

        filter_expr_out = filter_expr_out.replace(els, '('+els_out+')')

    return filter_expr_out

def optimade_filter_conversion(filter_expr):
    """
    Convert optimade filters to oqmdap formationenergy filters
    Input:
        :str : original filter expression
    Output:
        :str : converted filter expression
    """
    filter_expr_out = filter_expr

    # General conversion
    filter_expr_out = filter_expr_out.replace('_oqmd_', '')
    filter_expr_out = filter_expr_out.replace('&', 'AND')
    filter_expr_out = filter_expr_out.replace('|', 'OR')
    # Convert 'elements=' into mutiple 'element=' filters
    for els in re.findall('elements=[^-0-9\/]+', filter_expr):
        els_out = els.replace('elements=', '')

        els_lst = [' element='+e+' ' for e in els_out.split(',')]

        els_out = ' AND '.join(els_lst)

        filter_expr_out = filter_expr_out.replace(els, '('+els_out+')')


    return filter_expr_out



def query_to_Q(query_string):

    """
        Function to convert expression into Q model
        Input: 
            :str expr: format should be 'attribute=value' e.g. 'element=Fe'
                list of valid attributes:
                    element, generic, prototype, spacegroup,
                    volume, natoms, ntypes, stability,
                    delta_e, band_gap, chemical_formula
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

    if 'element_set' in query_string:
        query_string = element_set_conversion(query_string)
    query_string = optimade_filter_conversion(query_string)
    dlconverter  = Lark2Django()
    parsed_tree  = dlconverter.parse_raw_q(query_string)
    return dlconverter.evaluate(parsed_tree)
