=========
Tutorials
=========

.. automodule:: qmpy

The qmpy package comes bundled with two executable scripts, `qmpy` and `oqmd`. 
`qmpy` is a simple bash script that starts an interactive python
environment and imports qmpy::

    $ qmpy
    >>>

To write your own python script that utilizes qmpy functionality, simply start
with an import like::
    
    from qmpy import *

and all of the commands shown below should work.

Database entries
----------------

Once the database is `installed <getting_started>`_, you can query it very
flexibly and easily. In this section we will explore the data structure of
entries in the OQMD and provide several examples of how to make queries.
For deeper understanding of how django models work, you should check out the
(excellent) `django documentation <http://docs.djangoproject.com/en/1.6/>`_.

First, lets look at how to access an entry from the database. As an example,
lets pull up an entry for an :mod:`~qmpy.Element`::

    >>> fe = Element.objects.get(symbol='Fe')
    >>> fe
    <Element: Fe>

Django models have a number of fields that can be accessed directly once the
database entry has been loaded. For example, with an element you can::

    >>> fe.symbol
    u'Fe'
    >>> fe.z
    26L

For a complete list of the model attributes that are stored in the database,
refer to the documentation for the model you are interested in, in this case
:mod:`~qmpy.Element`. 

.. note::
    When strings are returned, they are returned as unicode strings,
    (indicated by the "u" preceding the string) integers are
    returned as long integers (indicated by the trailing "L"). For most
    purposes this makes no difference, as these data types will generally
    behave exactly as expected, i.e.::

        >>> fe.z == 26
        True
        >>> fe.symbol == "Fe"
        True

In addition to data attributes like these, django models have relationships to
other models. In qmpy there are two flavors of relationships: one-to-many and
many-to-many. An example of a one-to-many relationship would be the
relationship between an :mod:`~qmpy.Element` and an :mod:`~qmpy.Atom`. 
There are many atoms which are a given element, but each atom is only 
one element. In the case of Fe::
    
    >>> fe.atom_set
    <django.db.models.fields.related.RelatedManager object at 0x7f0997fa2690>
    >>> fe.atom_set.count()
    127585
    >>> atom = fe.atom_set.first()
    >>> print atom
    <Atom: Fe @ 0.000000 0.000000 0.000000>
    >>> atom.element
    <Element: Fe>

A :class:`RelatedManager` is an object that deals with obtaining other django models 
that are related to the main object. We can use the objects.count() method to
fidn the number of :mod:`~qmpy.Atom` objects that are Fe, and find ~125,000. 
To obtain one of these atoms, we use the objects.first() method, which 
simply returns the first :mod:`~qmpy.Atom` which is Fe. Much more functionality of Managers 
and RelatedManagers will be shown throughout this tutorial and in the examples,
but for a proper understanding you should refer to the django docs.

An example of a many-to-many relationship would be the relationship between an
:mod:`~qmpy.Element` and a :mod:`~qmpy.Composition`. A composition (e.g. Fe2O3) 
can contain many elements (Fe and O), and an element can be a part of many 
compositions (Fe3O4 and FeO as well). This is the nature of a many-to-many 
relationship. In the case of Fe::
    
    >>> fe.composition_set.count()
    10882
    >>> comp = fe.composition_set.filter(ntypes=2)[0]
    >>> comp
    <Composition: AcFe>
    >>> comp.element_set.all()
    [<Element: Ac>, <Element: Fe>]

In this example we have taken our base object (the :mod:`~qmpy.Element`) and filtered its
composition_set for :mod:`~qmpy.Composition` objects which meet the condition ntypes=2 (i.e.
there are two elements in the composition), and taken the first such
:class:`Composition` (index 0 in the :class:`QuerySet` that is returned). 
    
Creating a structure
--------------------

There are several ways to create a structure, but we will start with reading in
a POSCAR::
    
    >>> s = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')

Once you have the :mod:`~qmpy.Structure` object, the important features of a crystal
structure can be accessed readily.::

    >>> s.cell
    array([[ 3.,  0.,  0.],
           [ 0.,  3.,  0.],
           [ 0.,  0.,  3.]])
    >>> s.lat_params
    [3.0, 3.0, 3.0, 90.0, 90.0, 90.0]
    >>> s.atoms
    [<Atom: Cu @ 0.000000 0.000000 0.000000>, <Atom: Cu @ 0.500000 0.500000
    0.500000>]
    >>> s.composition
    <Composition: Cu>
    >>> s.volume
    27.0

You can also readily construct a :mod:`~qmpy.Structure` from scratch, from the lattice
vectors and the atom positions.::
    
    >>> s2 = Structure.create([3,3,3], [('Cu', [0,0,0]), 
                                        ('Cu', [0.5,0.5,0.5])])
    >>> s2 == s
    True

First Principles Calculations
-----------------------------

At this time qmpy only supports automation of calculations using the Vienna Ab
Initio Simulation Package (VASP). The reading and creation of these
calculations are handled by the :mod:`~qmpy.Calculation` model. 
To read in an existing calculation::

    >>> path = '/analysis/vasp/files/normal/fine_relax/'
    >>> calc = Calculation.read(INSTALL_PATH+path)

qmpy will search the directory for an OUTCAR or OUTCAR.gz file. If it is able
to find an OUTCAR, it will attempt to read the file. Next, we will demonstrate
several of the key attributes you may wish to access::

    >>> calc.energy # the final total energy
    -12.416926999999999 
    >>> calc.energies # the total energies of each step
    array([-12.415236 -12.416596, -12.416927])
    >>> calc.volume # the output volume
    77.787375068172508
    >>> calc.input
    <Structure: SrGe2>
    >>> calc.output
    <Structure: SrGe2>
    >>> from pprint import pprint
    >>> pprint(calc.settings)
    {'algo': 'fast',
     'ediff': 0.0001,
     'encut': 373.0,
     'epsilon': 1.0,
     'ibrion': 1,
     'idipol': 0,
     'isif': 3,
     'ismear': 1,
     'ispin': 1,
     'istart': 0,
     'lcharg': True,
     'ldipol': False,
     'lorbit': 0,
     'lreal': False,
     'lvtot': False,
     'lwave': False,
     'nbands': 24,
     'nelm': 60,
     'nelmin': 5,
     'nsw': 40,
     'potentials': [{'name': 'Ge_d', 'paw': True, 'us': False, 'xc': 'PBE'},
                    {'name': 'Sr_sv', 'paw': True, 'us': False, 'xc': 'PBE'}],
     'potim': 0.5,
     'prec': 'med',
     'pstress': 0.0,
     'sigma': 0.2}

