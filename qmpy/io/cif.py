# qmpy/io/cif.py

import numpy as np
from CifFile import ReadCif, CifFile, CifBlock
import itertools
import logging

import qmpy
import qmpy.materials.structure as strx
import qmpy.materials.composition as comp
import qmpy.analysis.symmetry as sym
import qmpy.data.reference as rx
from qmpy.utils import *

logger = logging.getLogger(__name__)

elt_regex = re.compile('([A-Z][a-z]?)')

class CifError(Exception):
    pass

def _get_value(number):
    """Attempt to return a float from a cif number value."""
    if number == '.':
        return 0.0
    if number == '?':
        return None
    try:
        return float(number)
    except ValueError:
        pass
    number = number.split('(')[0]
    return float(number)

def _get_element(atom):
    if hasattr(atom, '_atom_site_type_symbol'):
        return elt_regex.findall(atom._atom_site_type_symbol)[0]
    elif hasattr(atom, '_atom_site_label'):
        return elt_regex.findall(atom._atom_site_label)[0]
    else:
        raise Exception('No recognized element identifier')

def _get_atom_coord(atom):
    if '_atom_site_fract_x' in atom.__dict__:
        x = _get_value(atom._atom_site_fract_x)
        y = _get_value(atom._atom_site_fract_y)
        z = _get_value(atom._atom_site_fract_z)
        return [x,y,z]

def _get_occupancy(atom):
    if '_atom_site_occupancy' in atom.__dict__:
        occ = _get_value(atom._atom_site_occupancy)
        if not occ is None:
            return occ
    return 1.0

def _get_b_factor(atom):
    if '_atom_site_B_iso_or_equiv' in atom.__dict__:
        b = atom._atom_site_B_iso_or_equiv
        if not b is None:
            return b
    return 1.0

def _get_atom(cba):
    """Convert a _atom loop to an Atom"""
    atom = strx.Atom()
    atom.element_id = _get_element(cba)
    if atom.element_id == 'D' or atom.element_id == 'T':
        atom.element_id = 'H'

    atom.coord = _get_atom_coord(cba)
    atom.occupancy = _get_occupancy(cba)
    atom.b_factor = _get_b_factor(cba)
    return atom

def _get_lattice_parameters(cb):
    """Return a tuple of lattice parameters from a CifBlock."""
    return (_get_value(cb.get('_cell_length_a')),
            _get_value(cb.get('_cell_length_b')),
            _get_value(cb.get('_cell_length_c')),
            _get_value(cb.get('_cell_angle_alpha')),
            _get_value(cb.get('_cell_angle_beta')),
            _get_value(cb.get('_cell_angle_gamma')))

def _get_oxidation_state_data(cb):
    if '_atom_type_symbol' in cb.keys():
        cl = cb.GetLoop('_atom_type_symbol')
        if '_atom_type_oxidation_number' in cl.keys():
            symbols = [l._atom_type_symbol for l in cl]
            ox = [l._atom_type_oxidation_number for l in cl]
            return dict(zip(symbols, map(_get_value, ox)))
    else:
        return {}

def _get_sym_ops(cb):
    '''
    Load symmetry operations out of the cif file.

    Defaults to using the symmetry operations specified
    in the cif file (e.g., using "_space_group_symop_operation_xyz").
    Otherwise, will read the space group information

    Input:
        cb - CifFile, Cif being parsed
    Output:
        [rotation matrix, translation matrix] - A 2-member
        list containing the rotation and translation matrices
    '''
    if '_symmetry_equiv_pos_as_xyz' in cb.keys():
        rots, trans = [], []
        for op in cb.GetLoop('_symmetry_equiv_pos_as_xyz'):
            r, t = parse_sitesym(op._symmetry_equiv_pos_as_xyz)
            rots.append(r)
            trans.append(t)
        return [rots, trans]
    if '_space_group_symop_operation_xyz' in cb.keys():
        rots, trans = [], []
        for op in cb.GetLoop('_space_group_symop_operation_xyz'):
            r, t = parse_sitesym(op._space_group_symop_operation_xyz)
            rots.append(r)
            trans.append(t)
        return [rots, trans]
    if '_symmetry_int_tables_number' in cb.keys():
        try:
            sg = cb.get('_symmetry_int_tables_number')
            sg = sym.Spacegroup.objects.get(number=sg.strip())
            return [sg.rotations, sg.translations]
        except Exception, err:
            print err
            pass
    if '_[local]_cod_cif_authors_sg_H-M' in cb.keys():
        try:
            sg = cb.get('_[local]_cod_cif_authors_sg_H-M')
            sg = sym.Spacegroup.objects.get(hm=sg.strip())
            return [sg.rotations, sg.translations]
        except Exception, err:
            print err
            pass
    if '_symmetry_space_group_name_Hall' in cb.keys():
        try:
            sg = cb.get('_symmetry_space_group_name_Hall')
            sg = sym.Spacegroup.objects.get(hall=sg.strip())
            return [sg.rotations, sg.translations]
        except Exception, err:
            print err
            pass
    if '_space_group_name_Hall' in cb.keys():
        try:
            sg = cb.get('_space_group_name_Hall')
            sg = sym.Spacegroup.objects.get(hall=sg.strip())
            return [sg.rotations, sg.translations]
        except Exception, err:
            print err
            pass
    if '_symmetry_space_group_name_H-M' in cb.keys():
        try:
            sg = cb.get('_symmetry_space_group_name_H-M')
            sg = sym.Spacegroup.objects.get(hm=sg.strip())
            return [sg.rotations, sg.translations]
        except Exception, err:
            print err
            pass
    return [np.eye(3)], [np.array([0,0,0])]

def _read_cif_block(cb):
    s = strx.Structure()
    s.cell = latparams_to_basis(_get_lattice_parameters(cb))
    sym_ops = _get_sym_ops(cb)

    ox_data = _get_oxidation_state_data(cb)

    for atom in cb.GetLoop('_atom_site_label'):
        na = _get_atom(atom)
        if ox_data:
            na.ox = ox_data.get(atom._atom_site_type_symbol, None)
        for rot, trans in zip(*sym_ops):
            coord = np.dot(rot, na.coord) + trans
            coord = wrap(coord)
            a = na.copy()
            a.coord = coord
            s.add_atom(a, tol=1e-1)

    s.composition = comp.Composition.get(s.comp)
    
    ## meta data
    s.r_val = float(cb.get('_refine_ls_R_factor_all', 0.0))
    s.temperature = _get_value(cb.get('_cell_measurement_temperature', 0.0))
    s.pressure = _get_value(cb.get('_cell_measurement_pressure', 0.0))
    if cb.get('_chemical_name_structure_type'):
        s.prototype = strx.Prototype.get(cb.get('_chemical_name_structure_type'))
    try:
        s.reported_composition = strx.Composition.get(
                       parse_comp(cb.get('_chemical_formula_sum')))
    except:
        pass
    s.input_format = 'cif'
    s.natoms = len(s)
    s.get_volume()
    return s

def _add_comp_loop(structure, cb):
    c_cols = [[ '_atom_type_symbol', '_atom_type_oxidation_number' ]]
    c_data = [[ [ str(s) for s in structure.species ],
                [ str(s.ox_format) for s in structure.species ] ]]
    cb.AddCifItem(( c_cols, c_data ))

def _add_cell_loop(structure, cb):
    a, b, c, alpha, beta, gamma = structure.lat_params
    cb['_cell_length_a'] = '%08f' % a
    cb['_cell_length_b'] = '%08f' % b
    cb['_cell_length_c'] = '%08f' % c
    cb['_cell_angle_alpha'] = '%08f' % alpha
    cb['_cell_angle_beta'] = '%08f' % beta
    cb['_cell_angle_gamma'] =  '%08f' % gamma
    cb['_cell_volume'] = '%08f' % structure.get_volume()

def _add_symmetry_loop(structure, cb, wrap=False):
    structure.group_atoms_by_symmetry()
    data = sym.get_symmetry_dataset(structure)
    eqd = dict( (i, e) for i, e in enumerate(data['equivalent_atoms']) )
    cb['_symmetry_space_group_name_H-M'] = str(data['international'])
    cb['_symmetry_Int_Tables_number'] = str(data['number'])
    ss_cols = [[ '_symmetry_equiv_pos_site_id', '_symmetry_equiv_pos_as_xyz']]
    ss_data = [[ [ str(i+1) for i in range(len(data['rotations'])) ],
                 [ str(sym.Operation.get((r, t))) for r, t in 
                             zip(data['rotations'], data['translations']) ] ]]
    cb.AddCifItem(( ss_cols, ss_data ))
    a_rows = [[ '_atom_site_label', '_atom_site_type_symbol',
                '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z', 
                '_atom_site_Wyckoff_symbol',
                '_atom_site_occupancy' ]]
    a_data = [ [ str('%s%d' % (a.element_id, eqd[i])) 
                      for i, a in enumerate(structure)],
                [ str('%s%+d' % (a.element_id, 
                    a.ox if a.ox else 0 ))
                                 for a in structure ],
                [ '%08f' % a.x for a in structure ], 
                [ '%08f' % a.y for a in structure ], 
                [ '%08f' % a.z for a in structure ], 
                [ str(data['wyckoffs'][i]) for i in range(len(structure)) ],
                [ '%08f' % a.occupancy for a in structure ] ]

    if wrap:
        tmparr = np.array(a_data).T.tolist()
        for a in list(tmparr):
            for i, j, k in itertools.product([0, 1], [0, 1], [0, 1]):
                if i == 0 and j == 0 and k == 0:
                    continue
                if ( float(a[2])+i <= 1 and 
                     float(a[3])+j <= 1 and
                     float(a[4])+k <= 1):
                    tmparr.append([ a[0], a[1], 
                        '%08f' % (float(a[2])+i),
                        '%08f' % (float(a[3])+j),
                        '%08f' % (float(a[4])+k),
                        a[5], a[6]])
        tmparr = sorted(tmparr, key=lambda x: x[0])
        a_data = np.array(tmparr).T.tolist()
    cb.AddCifItem(( a_rows, [a_data] ))

def _add_header(structure, cb):
    form_sum = ''
    for k, v in structure.comp.items():
        form_sum += '%s%s' % (k, v)

    cb.AddCifItem(('_chemical_formula_sum', form_sum))

def _make_cif_block(structure, wrap=False):
    cb = CifBlock()
    _add_header(structure, cb)
    _add_cell_loop(structure, cb)
    _add_symmetry_loop(structure, cb, wrap=wrap)
    _add_comp_loop(structure, cb)
    return cb

def write(structures, filename=None, wrap=False, **kwargs):
    """
    Write a structure or list of structures to a cif file.

    Arguments:
        structures: 
            A :mod:`~qmpy.Structure` object or list of objects. If supplied
            with several Structures, they will all be written to the same cif.

    Keyword Arguments:
        filename:
            If supplied with a file name, will write to the file. If no
            filename is given, will return a string.
        wrap:
            If True, will include atoms at fractional coordinates 0 and 1.
            Useful only for visualizing structures.

    Examples::

        >>> io.cif.write(structure, "test.cif")
        >>> io.cif.write([structure1, structure2], "test.cif")

    """
    cif = CifFile()
    if not isinstance(structures, list):
        structures=[structures]
    for i, structure in enumerate(structures):
        cif['structure_%d' % i ] = _make_cif_block(structure, wrap=wrap)
    
    if filename:
        open(filename, 'w').write(str(cif))
    else:
        return str(cif)

def read(cif_file, grammar=None):
    """
    Takes a CIF format file, and returns a Structure object. Applies all
    symmetry operations in the CIF to the atoms supplied with the structure. If
    these are not correct, the structure will not be either. If the CIF
    contains more than one file, the return will be a list. If not, the return
    will be a single structure (not in a len-1 list).

    Examples::

        >>> s = io.cif.read(INSTALL_PATH+'io/files/fe3o4.cif')

    """
    if grammar:
        cf = ReadCif(cif_file, grammar=grammar)
    else:
        cf = ReadCif(cif_file)
    structures = []
    for key in cf.keys():
        structures.append(_read_cif_block(cf[key]))
    if len(structures) == 1:
        return structures[0]
    else:
        return structures

def _get_journal(cb):
    if '_citation_journal_id_ASTM' in cb.keys():
        code = cb.get('_citation_journal_id_ASTM')[0]
        j, new = rx.Journal.objects.get_or_create(code=code)
        if new:
            j.name = cb.get('_citation_journal_full')[0]
        return j
    elif '_journal_name_full' in cb.keys():
        name = cb.get('_journal_name_full')
        j, new = rx.Journal.objects.get_or_create(name=name)
        return j

def _get_authors(cb):
    auths = []
    if '_publ_author_name' in cb.keys():
        for name in cb.get('_publ_author_name'):
            auths.append(rx.Author.from_name(name))
    return auths

def _get_year(cb):
    if '_citation_year' in cb.keys():
        return cb.get('_citation_year')[0]
    elif '_journal_year' in cb.keys():
        return cb.get('_journal_year')

def _get_volume(cb):
    if '_citation_journal_volume' in cb.keys():
        return cb.get('_citation_journal_volume')[0]
    elif '_journal_volume' in cb.keys():
        return cb.get('_journal_volume')

def _get_first_page(cb):
    if '_citation_page_first' in cb.keys():
        return cb.get('_citation_page_first')[0]
    elif '_journal_page_first' in cb.keys():
        return cb.get('_journal_page_first')

def _get_last_page(cb):
    if '_citation_page_last' in cb.keys():
        return cb.get('_citation_page_last')[0]
    elif '_journal_page_last' in cb.keys():
        return cb.get('_journal_page_last')

def _get_title(cb):
    if '_publ_section_title' in cb.keys():
        return cb.get('_publ_section_title').strip()

def read_reference(cif_file):
    """
    Read a cif file and return a :mod:`~qmpy.Reference`.
    """
    cf = ReadCif(cif_file, grammar='1.1')
    cif_block = cf[cf.keys()[0]]
    reference = rx.Reference()
    reference.authors = _get_authors(cif_block)
    reference.journal = _get_journal(cif_block)
    reference.volume = _get_volume(cif_block)
    reference.year = _get_year(cif_block)
    reference.first_page = _get_first_page(cif_block)
    reference.last_page = _get_last_page(cif_block)
    reference.title = _get_title(cif_block)
    return reference
