# -*- coding: utf-8 -*-

import cif
import poscar
import ase
import ase.io

class StructureFormatError(Exception):
    """Problem reading an input file"""

class FormatNotSupportedError(Exception):
    """The provided input format is not supported"""

def read(source_file, *args, **kwargs):
    """
    Read an input file of various formats.

    Arguments:
        source_file:
            The first argument is a structure file of some format.

    The remaining args and kwargs are passed to the methods called to read the
    structure.

    If the structure name contains "cif" or "POSCAR" it will be read as one of
    these formats. Failing that, the file is passed to the ASE read method, and
    the returned Atoms object is then converted to a Structure.

    Examples::

        >>> io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
        >>> io.read(INSTALL_PATH+'/io/files/fe3o4.cif')

    """
    try:
        if 'cif' in source_file:
            return cif.read(source_file, *args, **kwargs)
        elif ( 'POSCAR' in source_file or
                'CONTCAR' in source_file ):
            return poscar.read(source_file, *args, **kwargs)
        else:
            return ase.io.read(source_file, *args, **kwargs)
    except:
        try:
            return poscar.read(source_file, *args, **kwargs)
        except Exception:
            pass
        try:
            return cif.read(source_file, *args, **kwargs)
        except Exception:
            pass
    raise FormatNotSupportedError('The file %s is in an unrecognized format\
            and cannot be read' % source_file)

def write(structure, format='poscar', convention=None, filename=None,
        **kwargs):
    """
    Write the `~qmpy.Structure` object to a file or string.

    Arguments:
        structure: `~qmpy.Structure` object.

    Keyword Arguments:
        format:
            If the format is "poscar" or "cif", call poscar.write or cif.write
            respectively. Otherwise, converts the Structure to a
            :mod:`~ase.Atoms` object and calls the :func:`ase.io.write` method
            with all arguments and keywords passed to that function.

        convention:
            Takes three values, "primitive", "conventional" or None. If
            "primitive" converts the structure to its primitive cell. If
            "conventional" converts the structure to its conventional cell. If
            None, writes the structure as is.

        filename:
            Filename to write to. If None, returns a string.

    Returns:
        None or a string.

    """
    if convention == 'primitive':
        structure.make_primitive()
    elif convention == 'conventional':
        structure.make_conventional()

    def write_or_return(string, filename=None):
        if filename is None:
            return string
        else:
            f = open(filename, 'w')
            f.write(string)
            f.close()

    if format == 'poscar':
        return write_or_return(poscar.write(structure, **kwargs), filename)
    elif format == 'cif':
        return write_or_return(cif.write(structure, **kwargs), filename)
    else:
        return write_or_return(ase_mapper.write(structure, **kwargs), filename)
