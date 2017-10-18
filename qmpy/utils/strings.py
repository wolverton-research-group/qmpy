"""
qmpy.data.strings

Contains useful functions for string manipulation. Some important conventions
observed throughout qmpy that are particularly relevent here:
    names are of the form: is FeO2 Ni3B
    formula are of the form: Fe,O2 Ni3,B
    comp are of the form: {'Fe':1, 'O':2} {'Ni':3, 'B':1}
    latex are of the form: FeO_2 Ni_3B

These forms can be converted between with x_to_y functions, where x can be
name, formula, comp or latex. (latex and only be y)

"""
from collections import defaultdict
import itertools
import numpy as np
import re
import yaml
import fractions as frac
import decimal as dec
import logging

import qmpy
from qmpy.utils.math import *
import qmpy.data as data

logger = logging.getLogger(__name__)

## regex's
re_comp = re.compile('({[^}]*}[,0-9x\.]*|[A-Z][a-wyz]?)([,0-9x\.]*)')
spec_comp = re.compile('([A-Z][a-z]?)([0-9\.]*)([+-]?)')
re_formula = re.compile('([A-Z][a-z]?)([0-9\.]*)')
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

## Parsing

def is_comp(value):
    new_value = str(value)
    for elt, amt in re_formula.findall(value):
        new_value = new_value.replace(elt, '')
        new_value = new_value.replace(amt, '')
    if new_value:
        return False
    else:
        return True


def parse_mu(value):
    if '=' in value:
        elt, pot = value.split('=')
        if ':' in pot:
            pot = map(float, pot.split(':'))[:2]
        else:
            pot = float(pot)
    else:
        elt = value
        pot = 0.0
    return {elt: pot}

def parse_comp(value):
    comp = defaultdict(float)
    for elt, amt in re_formula.findall(value):
        if elt in ['D', 'T']:
            elt = 'H'
        if amt == '':
            comp[elt] = 1
        elif is_integer(amt):
            comp[elt] += int(round(float(amt)))
        else:
            comp[elt] += float(amt)
    return dict(comp)

def parse_space(value):
    if isinstance(value, basestring):
        space = re.sub('[-,_]', ' ', value)
        space = [ unit_comp(parse_comp(b)) for b in space.split()]
    elif isinstance(value, (list,set)):
        space = [ {elt:1} for elt in value ]
    elif isinstance(value, dict):
        space = [ {elt:1} for elt in value ]
    elif not value:
        space = None
    else:
        raise ValueError("Failed to parse space: %s" % value)
    return space

def parse_sitesym(sitesym, sep=','):
    rot = np.zeros((3, 3), dtype='int')
    trans = np.zeros(3)
    for i, s in enumerate (sitesym.split(sep)):
        s = s.lower().strip()
        while s:
            sign = 1
            if s[0] in '+-':
                if s[0] == '-':
                    sign = -1
                s = s[1:]
            if s[0] in 'xyz':
                j = ord(s[0]) - ord('x')
                rot[i, j] = sign
                s = s[1:]
            elif s[0].isdigit() or s[0] == '.':
                n = 0
                while n < len(s) and (s[n].isdigit() or s[n] in '/.'):
                    n += 1
                t = s[:n]
                s = s[n:]
                trans[i] = float(frac.Fraction(t))
            else:
                raise ValueError('Failed to parse symmetry of %s' % (sitesym))
    return rot, trans

def parse_species(value):
    elt, charge, sign = spec_comp.findall(value)[0]
    if charge == '':
        return elt, None
    elif is_integer(charge):
        charge = int(charge)
    else:
        charge = float(charge)

    if sign in ['+', '']:
        return elt, charge
    elif sign == '-':
        return elt, -1*charge

## Formatting

def format_mus(mus):
    name = ''
    for k, v in mus.items():
        if name:
            name += ' '
        name += k
        if v is None:
            continue
        if isinstance(v, (float, int)):
            name += '=%.3g' % v
        elif isinstance(v, list):
            name += '=%.3g:%.3g' % tuple(v)
        else:
            raise TypeError('Unrecognized format for mus:', mus)
    return name

def format_species(element, value):
    if value is None:
        return element
    if is_integer(value):
        ox = str(abs(int(value)))
    else:
        ox = str(abs(float(value))).rstrip('0.')
    name = '%s%s' % (element, ox)
    if value < 0:
        name += '-'
    else:
        name += '+'
    return name

def get_coeffs(values):
    wasdict = False
    if isinstance(values, dict):
        keys, values = zip(*values.items())
        wasdict = True

    coeffs = []
    for v in values:
        if v == 1:
            coeffs.append('')
        elif is_integer(v):
            coeffs.append('%d' % v)
        else:
            coeffs.append(('%.8f' % v).rstrip('0'))

    if wasdict:
        return dict(zip(keys, coeffs))
    else:
        return coeffs

def electronegativity(elt):
    if not elt in data.elements:
        return 0.0
    else:
        if not 'electronegativity' in data.elements[elt]:
            return 0.0
        return data.elements[elt]['electronegativity']

def format_comp(comp, template='{elt}{amt}', delimiter='',
        key=lambda x: (electronegativity(x), x)):
    elts = sorted(comp.keys(), key=key)
    coeffs = get_coeffs(comp)
    return delimiter.join(template.format(elt=k, amt=coeffs[k]) for k in elts)

def format_generic_comp(comp):
    amts = get_coeffs(sorted(comp.values()))
    gen_comp = zip(alphabet, amts)
    return ''.join('{elt}{amt}'.format(elt=elt, amt=amt) for elt, amt in
            gen_comp)

def format_html(comp):
    return format_comp(comp, template='{elt}<sub>{amt}</sub>')

def format_latex(comp):
    return format_comp(comp, template='{elt}$_{{{amt}}}$')

def format_bold_latex(comp):
    return format_comp(comp, template='{elt}$_{{\mathbf{{{amt}}}}}$')

def format_gnuplot(comp):
    return format_comp(comp, template='{elt}_{{{amt}}}')

def normalize_dict(dictionary):
    tot = float(sum(dictionary.values()))
    return dict((k, v/tot) for k,v in dictionary.items())

def unit_comp(comp):
    return normalize_dict(comp)

def reduce_by_gcd(values, tol=5e-2):
    least = min([ v for v in values if v ])
    ints = [roundclose(v/least, tol) for v in values ]
    gcd = reduce(frac.gcd, [roundclose(v, tol) for v in values if v ])
    return [ v/gcd for v in values ]

def reduce_by_partial_gcd(values):
    ints = [roundclose(v) for v in values if is_integer(v)]
    if not ints:
        return values
    least = min(ints)
    ints = [ v/least for v in ints ]
    gcd = reduce(frac.gcd, ints)
    return [ v/gcd for v in values ]

def reduce_by_any_means(values):
    i = 0
    d = 0
    vals = np.array([ roundclose(v) for v in values])
    primes = range(1, 10)
    while d < 1e-6:
        if i > len(primes)-1:
            vals = np.round(vals*10**3)/10**3
            break
        i += 1
        p = primes[i-1]
        d = reduce(frac.gcd, [ roundclose(v, 5e-2) for v in vals*p ])
    else:
        vals = np.round(vals*p/d)
    return vals.tolist()

def reduce_comp(values, method='auto'):
    """
    Attempt to construct a 'pretty' composition string.

    With the inclusion partial occupancy this process becomes more difficult to
    do consistently. This function calls several functions which attempt to
    find a "good" composition string, and attempts to discern which is best.

        b) If that fails (i.e. the GCD < 1e-10, and there is no accurate
        rational value ), try multiplying the coefficients by the first 20
        prime numbers. For example: if your coefficients are 
        [0.3333333, 0.6666667], this will fail to identify a rational GCD, but
        if you multiply by 3, you get [1, 2]. NOTE: This only works because we
        only keep compositions to 1 decimal place. As a result, 0.6666667
        cannot be properly identified, but 0.6666667*3, can. 

        c) If None of these work, simply return the literal composition given,
        rounded to 3 decimal places.

    Examples:
    >>> comp = {'Fe':1, 'O':1.5}
    >>> reduce_comp(comp)
    {'Fe':2, 'O':3}
    """

    if not values:
        return ''

    wasdict = False
    if isinstance(values, dict):
        keys, values = zip(*values.items())
        wasdict = True

    def make_return(values):
        if wasdict:
            return dict(zip(keys, map(roundclose, values)))
        else:
            return values

    first = reduce_by_gcd(values)
    if all( v < 1000 for v in first):
        return make_return(first)

    ints = [ v for v in values if is_integer(v) ]
    second = reduce_by_partial_gcd(values)
    if len(ints) == len(values) - 1:
        return make_return(second)

    if sum(values) <= 1.005:
        third = reduce_by_any_means(values)
        if all( v < 1000 for v in third):
            return make_return(third)
    return make_return(second)

def normalize_comp(values):
    wasdict = False
    if isinstance(values, dict):
        keys, values = zip(*values.items())
        wasdict = True

    vals = np.array(values)
    vals /= min(vals)

    if wasdict:
        return dict(zip(keys, vals))
    else:
        return vals.tolist()

def parse_formula_regex(formula):
    """Take in a generalized expression for a composition. Use symbols for
    groups of elements for combinatorial replacements.

    Groups of elements can be identified by:
        - valence shell: 3d, 5s, 2p, etc...
        - group: G1 (alkali), G17 (halides), G4 (2d2), etc...
        - row: R1, R3
        - block: DD (all d-block), PP (all p-block), etc...

    Examples:
    >>> parse_formula_regex('Fe2O3')
    [{'Fe':2, 'O':3}]
    >>> parse_formula_regex('{Fe,Ni}2O3')
    [{'Fe':2, 'O':3}, {'Ni':2, 'O':3}]
    >>> parse_formula_regex('{3d}2O3')
    [{'Co': 2.0, 'O': 3.0}, {'Cr': 2.0, 'O': 3.0}, {'Cu': 2.0, 'O':3.0}, 
    {'Fe': 2.0, 'O': 3.0}, {'Mn': 2.0, 'O': 3.0}, {'Ni': 2.0, 'O': 3.0},
    {'Sc': 2.0, 'O': 3.0}, {'O': 3.0, 'Ti': 2.0}, {'O': 3.0, 'V': 2.0}, 
    {'Zn':2.0, 'O': 3.0}]

    """
    formulae = []
    sfind = re.compile('({[^}]*}[,0-9x\.]*|[A-Z][a-wyz]?[,0-9x\.]*)')
    matches = sfind.findall(formula)
    for term in matches:
        if '{' in term:
            symbols, amt = term.replace('{','').split('}')
            symbols = symbols.split(',')
            elts = []
            for symbol in symbols:
                if symbol in data.element_groups.keys():
                    elts += [ e for e in data.element_groups[symbol] ]
                else:
                    elts += [ symbol ]
            formulae.append([ e+amt for e in elts ])
        else:
            formulae.append([term])
    return [ parse_comp(''.join(ref)) for ref in itertools.product(*formulae) ]

def read_compressed_array(string):
    if '-' in string:
        first = string.startswith('-')
        string = string.lstrip('-')
        vals = map(lambda x: -float(x), string.split('-'))
        if not first:
            vals[0] = -vals[0]
        return vals

def read_fortran_array(string, expected_cols=None):
    """
    Attempts to read a fortran formatted list of numbers.

    .. Note:: Because fortran doesn't do a good job with ensuring that numbers
        are properly space delimited, this can fail.

    Returns:
        A list of floats.

    Raises: 
        ValueError: If the string cannot be parsed into the desired number of
        columns of numbers, a ValueError is raised.

    """
    arr = []
    for elt in string.split():
        try:
            elt = float(elt)
            arr.append(elt)
        except ValueError:
            elts = read_compressed_array(elt)
            arr += elts
    if expected_cols:
        if len(arr) != expected_cols:
            raise ValueError
    return arr
