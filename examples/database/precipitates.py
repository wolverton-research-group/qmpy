from qmpy import *
from django.db.models import Max

data = {
        'HCP':{
            'Mg': {
                'a': 3.193*2, 
                'c': 5.185,
                'hd':0.05},
            'Ti': {
                'a': 2.912*2, 
                'c': 4.620,
                'hd':0.05}},
        'FCC':{
            'Ni': {
                'a': 3.456,
                'lm': 0.05},
            'Co': {
                'a': 3.448,
                'lm': 0.05,
                'hd': 0.1},
            'Al': {
                'a': 4.04,
                'lm':0.1}},
        'BCC':{
            'Fe': {
                'a': 2.82,
                'lm': 0.05,
                'hhi': 6000},
            'Ti': {
                'a': 3.23, 
                'lm':0.05, 
                'hhi': 6000}}}

precips = {'BCC':'heusler','FCC':'L1_2', 'HCP':'D0_19'}

cols = {'BCC':{'a':'calculation__input__x2'}, 
        'FCC':{'a':'calculation__input__x1'},
        'HCP':{'a':'calculation__input__x1', 'c':'calculation__input__z3'}}

def apply_format(value):
    if isinstance(value, basestring):
        return value
    if value is True:
        return 'Yes'
    elif value is False:
        return 'No'
    try:
        value = float(value)
        if value < 500:
            return '%0.3f' % value
        else:
            return '%d' % int(round(value))
    except:
        return str(value)

def latex_table(contents, headers=[], units=[], title=''):
    result = '\\\\ \n'
    if title:
        result += title
    result += ('\\hline \\hline\n')
    result += ' & '.join(headers)+' \\\\ \n'
    result += ' & '.join(units)+' \\\\ \n'
    result += (
    '\\hline\n'
    '\\endfirsthead\n'
    '\n'
    '\multicolumn{'+str(len(headers))+'}'
    '{c}{{\\tablename} \\thetable{} -- Continued} \\\\ \n'
    '\\hline \\hline\n')
    result += ' & '.join(headers)+' \\\\ \n'
    result += ' & '.join(units)+' \\\\ \n'
    result += (
    '\\hline\n'
    '\\endhead\n'
    '\n'
    '\\multicolumn{'+str(len(headers))+'}'
    '{l}{{Continued on Next Page\\ldots}} \\\\ \n'
    '\\hline\n'
    '\\endfoot\n'
    '\n'
    '\\hline \\hline \n'
    '\\endlastfoot\n'
    )
    for line in contents:
        result += '    '+' & '.join([apply_format(v) for v in line])+' \\\\ \n'
    return result

def name(comp):
    comp = parse_comp(comp)
    coeffs = get_coeffs(comp)
    elts = sorted(comp.keys(), key=lambda x: (-comp[x], electronegativity(x)))
    return '$\\rm{'+''.join(['{elt}_{{{amt}}}'.format(elt=k, amt=coeffs[k]) for k in
        elts])+'}$'

def tabulate(elt, lattice):
    props = data[lattice][elt]
    results = json.loads(open('%s_%s.txt' % (elt, lattice)).read())
    headers = [ 'Compound', '$\\Delta H_f$', '$\Delta H_{stab}$', 'HHI' ]
    headers += [ '$\\Delta {%s}$' % a for a in props if a in [ 'a', 'b', 'c'] ]
    headers += [ 'In ICSD' ]
    units = [ '', 'eV/atom', 'eV/atom', '' ] + [ '\\%' for a in props if a in
            ['a', 'b', 'c' ] ] + []

    top = '\\multicolumn{%s}{l}{In equilibrium with %s} \\\\' % (len(headers)-1, elt)
    bot = '\\multicolumn{%d}{l}{Decomposes to %s} \\\\' % (len(headers), elt)
    content = []
    done = []
    for row in results:
        if not row['keep']:
            continue
        n = name(row['composition'])
        if n in done:
            continue
        trow = [n]
        done.append(n)
        if row['delta_e'] > -0.025:
            continue
        trow.append(row['delta_e'])
        trow.append(' --- ' if row['stability'] < 0 else row['stability'])
        trow.append(row['hhi'])
        for a in props:
            if a in ['a', 'b', 'c']:
                trow.append(row['lm'][a])
        trow.append(row['in_icsd'])
        content.append(trow)
    content = sorted(content, key=lambda x:(
        (0 if isinstance(x[2], basestring) else x[2]), x[3]))

    f = open('%s_%s.tex' % (lattice, elt), 'w')
    f.write(latex_table(content, headers, units))
    f.close()

def find(lattice):
    proto = Entry.objects.filter(meta_data__value=precips[lattice],
            duplicate_of=None)
    icsd = Entry.objects.filter(duplicates__meta_data__value=precips[lattice])
    results = proto | icsd
    nonmetals = Element.objects.exclude(
            symbol__in=element_groups['all-metals'])
    results = results.exclude(element_set__HHI_P=0)
    results = results.exclude(element_set__in=nonmetals)
    return results

def process(elt, lattice):
    pd = PhaseData()
    pd.load_oqmd(search={'delta_e__lte':0})

    props = data[lattice][elt]
    entries = find(lattice)
    forms = Formation.objects.filter(delta_e__lt=0, entry__in=entries.values('id'))
    forms = forms.annotate(hhi=Max('composition__element_set__HHI_P'))
    results = forms.values(*['entry', 'composition', 'delta_e', 'stability', 'hhi'] + 
        cols[lattice].values())
    if props.get('hhi'):
        results = results.filter(hhi__lt=props['hhi'])
    results = results.filter(stability__lt=props.get('hd', 0.025))
    lm = props.get('lm', 0.1)
    for k, v in cols[lattice].items():
        results = results.filter(**{v+'__lt':props[k]*(1+lm)})
        results = results.filter(**{v+'__gt':props[k]*(1-lm)})

    dicts = []
    done_comps = []
    for row in sorted(results, key=lambda x:x['delta_e']):
        row = dict(row)
        comp = parse_comp(row['composition'])
        name = format_comp(comp)
        if name in done_comps:
            continue
        else:
            done_comps.append(name)
        s = PhaseSpace(set([elt]) | set(comp.keys()), data=pd)
        row['lm'] = {}
        for k, v in cols[lattice].items():
            row['lm'][k] = 100*(row[v]-props[k])/props[k]

        if row['stability'] < 0:
            tie_line = set([s.phase_dict[name], s.phase_dict[elt]])
            if (tie_line in s.tie_lines):
                row['keep'] = True
            else:
                row['keep'] = False
        else:
            phases = [ p for k, p in s.phase_dict.items() if not k == name ]
            decomp = s.gclp(name, phases=phases)[1]
            if s.phase_dict[elt] in decomp.keys():
                row['keep'] = True
            else:
                row['keep'] = False

        # is in the ICSD?
        row['in_icsd'] = False
        if Entry.objects.filter(duplicate_of=row['entry'],
                label__contains='icsd').exists():
            row['in_icsd'] = True
        elif Entry.objects.filter(id=row['entry'], label__contains='icsd').exists():
            row['in_icsd'] = True

        dicts.append(row)

    open('%s_%s.txt' % (elt, lattice), 'w').write(json.dumps(dicts))

if __name__ == '__main__':
    for lattice, elts in data.items():
        for elt, props in elts.items():
            print '%s: %s' % (elt, lattice)
            if len(sys.argv) == 1 or sys.argv[1] == 'table':
                tabulate(elt, lattice)
            elif sys.argv[1] == 'data':
                process(elt, lattice)
