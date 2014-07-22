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


Searching for models
--------------------

The documentation for Django for searching for models is ver complete, and
should be taken as the ultimate reference for searching for models in qmpy, but
a basic overview is provided here. Specific methods used in this section are
the 'filter', 'exclude' and 'get' methods. 

Searches using filter will, as the name suggests, filter for database entries
that have the specified properties. Similarly, exclude will return entries that
do NOT have the specified properties. Both of these methods will return a
QuerySet containing any objects that meet the requirements of your search.
Filter and exclude calls can be chained together to create relatively complex
queries. Get is slightly different in that it returns ONLY ONE object, and
returns the object itself, rather than a QuerySet of such objects.

A much more complete documentation of all things query related can be found at
the `django docs <https://docs.djangoproject.com/en/dev/topics/db/queries/>`_

Searching for entries based on stability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Formation energies are stored as FormationEnergy instances, which are
associated with an `:mod:~qmpy.Entry` and a `:mod:~qmpy.Calculation`. Knowing
this, we can search for stable Entries using::

    >>> stable = Entry.objects.filter(formationenergy__stability__lt=0)
    >>> stable.count()
    18150

The same concept can be applied to searching for other quantities, as long as
you can relate them to a FormationEnergy by "__" constructions::

    >>> stable_comps = Composition.objects.filter(formationenergy__stability__lt=0)
    >>> stable_comps.count()
    18150
    >>> s = Structure.objects.filter(calculated__formationenergy__stability__lt=0)
    >>> s.count()
    18150

Adding other search criteria lets you explore a little more::

    >>> stable = FormationEnergy.objects.filter(stability__lt=0)
    >>> # Find the number of stable compounds containing O
    >>> stable.filter(composition__element_set='O').count()
    4017
    >>> # or Fe. Is it surprising that this is smaller?
    >>> stable.filter(composition__element_set='Fe').count()
    653
    >>> # Meta data is also a possiblity. How many stable compounds were found
    >>> # in the course of calculations for a particular project?
    >>> stable.filter(entry__project_set='prototypes').count()
    3119

Searching for entries based on composition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can find compositions in a few ways using filters and excludes. If you want
a specific region of phase space (including related subspaces)::

    >>> elts = [ 'Fe', 'Li', 'O' ]
    >>> others = Element.objects.exclude(symbol__in=elts)
    >>> comps = Composition.objects.exclude(element_set=others)

This searchs finds every composition that doesn't have any elements that aren't
in the region of phase space requested. For binary or ternary phase spaces it
can be more efficient to search permutations of sub-spaces::

    >>> comps = Composition.objects.filter(ntypes=3)
    >>> for e in elts:
    >>>     comps = comps.filter(element_set=e)
    >>> for e in elts:
    >>>     e_comps = Composition.objects.filter(element_set=e, ntypes=1)
    >>>     comps |= e_comps
    >>> for e1, e2 in itertools.combinations(elts, r=2):
    >>>     bin_comps = Composition.objects.filter(element_set=e1)
    >>>     bin_comps = bin_comps.filter(element_set=e2, ntypes=2)
    >>>     comps |= bin_comps
    >>> comps.distinct().count()

However, for larger regions of phase space (4 or 5 or more) the number of
subqueries of the second approach rapidly becomes more expensive than the
single, more complicated query of the first.

Advanced searching
------------------

The previous section covered some pretty basic methods for searching for
database entries. In this section we will look at some more advanced concepts,
specifically: aggregation, Q() and F().

Aggregation and Annotation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Django also provides methods for adding searchable and retrievable fields to
database entries within the SQL command. For example, suppose we want to search
for :mod:`~qmpy.Entry` objects that have more than 5 structures associated with
them. We can accomplish this using aggregation to add a temporary field to
Entries that is the number of structures. This temporary field can then be
filtered on and returned just like a normal field::
    
    >>> from django.db.models import Count, Average
    >>> entries = Entry.objects.annotate(n_structures=Count('structure'))
    >>> many_structs = entries.filter(n_structures__gt=5)
    >>> data = many_structs.values('id', 'path', 'n_structures')
    >>> print data[0]
    {'id': 1562L,
     'n_structures': 6,
     'path': u'/home/oqmd/libraries/prototypes/elements/C19/Ne'}

We can also do a variety of aggregation methods, also in SQL. Say we want to
know the average number of elements (averaged over all compositions in the
OQMD, or over ICSD structures)::
    
    >>> Composition.objects.aggregate(Avg('ntypes'))
    {'ntypes__avg': 2.9965}
    >>> Composition.objects.filter(entry__meta_data__value='icsd').\
                aggregate(Avg('ntypes'))
    {'ntypes__avg': 2.9811}

Complex searches
^^^^^^^^^^^^^^^^

When using sequential filter and exclude commands, these commands are related
by AND operators. In order to execute more complicated queries which use a
series of AND and OR operators, we must use the Q() method.::
    
    >>> from django.db.models import Q
    >>> query = Q(meta_data__value='prototype') | Q(meta_data__value='icsd')
    >>> Entry.objects.filter(query)

The Q() query method also supports negation, by calling ~Q()::
    
    >>> Composition.objects.filter(Q(ntypes=2) & 
                                   ~Q(element_set='O'))


Using qmpy to manage a high-throughput calculation project
----------------------------------------------------------

:mod:`qmpy` can manage almost every aspect of a high-throughput materials screening
project. In this section we will walk through all of the necessary steps to
get a new project off the ground in a new installation. This tutorial assumes
that you have a functional installation of :mod:`qmpy`, as well as a working
database (does not need to have a copy of the OQMD included, a blank slate
database will work fine).

In this tutorial we will undertake to explore a wide range of (CH3NH3)PbI3
perovskites, which have recently recieved much attention as high-efficiency
photovoltaic cells. We will run through the process of setting up compute
resources, constructing simple lattice decorations of this structure, as well
as some not-so-simple decorations, running the calculations, and finally
evaluating the relative stability of the resulting energies. 

Setting up computational resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We will begin with configuring qmpy to find the right computational resources
to be able to perform calculations using qmpy. First, you need to establish the
computational resources that are available to it: a :mod:`~qmpy.Account`, which is a
:mod:`~qmpy.Host` paired with a :mod:`~qmpy.User`. A :mod:`~qmpy.Account` is then granted
access to at least one :mod:`~qmpy.Allocation`. 

.. Warning::
   In the current implementation, qmpy is only able to run calculations on
   clusters that utilize PBS/torque and Maui.

Lets start by configuring a host. Lets assume that we are running qmpy from one
cluster, but we want to do our calculations on another machine. Lets edit the
resources/hosts.yml file (inside the qmpy installation)::


    # hosts.yml
    bigcluster:
      binaries: {vasp_53: /usr/local/bin/vasp_53}
      check_queue: /usr/local/maui/bin/showq
      hostname: big.cluster.edu
      ip_address: XXX.XX.XX.XXX
      nodes: 100
      ppn: 12
      sub_script: /usr/local/bin/qsub
      sub_text: bigcluster.q
      walltime: 691200

In this configuration file, we are creating a list of dictionaries. Each outer
loop entry creates a :mod:`~qmpy.Host`. 

Important attributes to be aware of:

* binaries is a dictionary of binary name -> binary path pairs. By default,
  qmpy calculations try to run vasp_53, and expects a path to a vasp 5.3.3
  binary, but should be reliable for most vasp 5.X versions.
* sub_script is the path on the cluster to pbs qsub command
* check_queue is the path on the cluster to maui's showq command
* sub_text is the name of a file in qmpy/configuration/qfiles. An example qfile
  template is shown below.
* ppn = # of processors / node
* nodes = # of nodes you want qmpy to be able to use (does not need to match
  the number of nodes on the cluster)

.. Note::
    Note that these files must be parseable YAML format files. See `this guide
    <http://www.yaml.org/start.html> _` for an introduction to the YAML format.


The queue files that qmpy submits must be tailored both to the job being
submitted and the cluster being submitted to. To that end, qmpy uses a simple
template system, with the most basic template (that should work in many cases)
is::

    #!/bin/bash
    #MSUB -l nodes={nodes}:ppn={ppn}
    #MSUB -l walltime={walltime}
    #MSUB -N {name}
    #MSUB -o jobout.txt
    #MSUB -e joberr.txt
    #MSUB -A {key}

    cd $PBS_O_WORKDIR
    NPROCS=`wc -l < $PBS_NODEFILE`
    #running on {host}

    {header}

    {mpi} {binary} {pipes}

    {footer}

The "{variable}" construction is used to automatically replace strings based on
the calculation requirements. Some variables (nodes, ppn, name, walltime, host)
are fairly constant for the host. Others, like "key", specify which allocation
to charge the hours to, which is defined by the :mod:`~qmpy.Allocation`
associated with the calculation. Finally, the rest of the variables are set
based on the requirements of the calculation. For general calculations, the
header variable is used to unzip any zipped files in the folder (e.g., CHGCAR),
the for parallel calculations the mpi variable contains the mpirun + argumnts
command and for serial calculations it is left blank. The binary variable will
be replaced with the path to the binary, as defined in the hosts.yml file. The
pipes variable will pipe stdout and stderr, which by default is always to
stdout.txt and stderr.txt. Finally, footer zips the CHGCAR, OUTCAR, PROCAR and
ELFCAR, if they exist.

and resources/hosts.yml::

    # users.yml
    oqmdrunner:
      bigcluster: {run_path: /home/oqmdrunner, username: oqmdrunner}

    oqmduser:
      bigcluster: {run_path: /home/oqmduser/rundir, username: oqmduser}
      smallcluster: {run_path: /home/oqmduser/rundir, username: oqmduser}

loop entry creates a :mod:`~qmpy.User` with that name, and each cluster listed
then creates an :mod:`~qmpy.Account` for that :mod:`~qmpy.User`, with username
(given by username) and configured to run calculations in run_path. Here we are
assuming that a second non-compute cluster, smallcluster, was also defined in
hosts.yml.

.. warning::
   Passwordless ssh must be configured to each account (either as a user:host 
   pair, or host-based authentication) from the account you are running qmpy
   on. The :mod:`~qmpy.Account` class has a create_passwordless_ssh method
   that can set this up for you, however, this process can be unreliable, so if
   it fails you will need to sort those problems out for yourself.

Next, we configure our allocations, using the allocations.yml file::

    # allocations.yml
    bigcluster:
      host: bigcluster
      users: [oqmdrunner, oqmduser]
      key: alloc1234

An allocation takes a host, a list of users and an optional key. The host and
list of users are used to determine who is allowed to run calculations on the
allocation, while the key is used to identify the allocation to moab, if that
feature is implemented.

Finally, we can create a :mod:`~qmpy.Project`, defined in projects.yml::

    # projects.yml
    example:
      allocations: [bigcluster]
      priority: 0
      users: [oqmdrunner]
    
We title the project "example", (since it is just an example) and then 
define the lists of allocations that this project is authorized to use, and the
users that are associated with the project. In order to apply these changes,
run::
    
    >>> from qmpy import *
    >>> sync_resources()


Working with Structures
^^^^^^^^^^^^^^^^^^^^^^^

If, for example, we say that we want to calculate i) a range of defects in a
host matrix or ii) a wide range of compositions in a particular structure. It
is possible to do this in the framework of qmpy, with minimal effort. Sadly,
our starting point, the CH3NH3PbI3 (since CH3NH3 is methylammonium, let us call
the compound MaPbI3 from now on) is not fully resolved in XRD. The best
structure I can find only has the Pb, C, N and I sites determined. So, lets
take this structure (reproduced here from Constantinos C. Stoumpos; et. al., 
Inorganic Chemistry 52 (2013) 9019-9038)::

    I C Pb N
     1.0
    8.849000 0.000000 0.000000
    0.000000 8.849000 0.000000
    0.000000 0.000000 12.642000
    C I N Pb
    4 12 4 4
    direct
     0.5000000000 0.0000000000 0.3520000000
     0.0000000000 0.5000000000 0.3520000000
     0.5000000000 0.0000000000 0.8520000000
     0.0000000000 0.5000000000 0.8520000000
     0.2858300000 0.2141700000 0.0046000000
     0.7858300000 0.2858300000 0.0046000000
     0.2141700000 0.7141700000 0.0046000000
     0.7141700000 0.7858300000 0.0046000000
     0.0000000000 0.0000000000 0.2472000000
     0.5000000000 0.5000000000 0.2472000000
     0.7141700000 0.2141700000 0.5046000000
     0.2141700000 0.2858300000 0.5046000000
     0.7858300000 0.7141700000 0.5046000000
     0.2858300000 0.7858300000 0.5046000000
     0.0000000000 0.0000000000 0.7472000000
     0.5000000000 0.5000000000 0.7472000000
     0.5000000000 0.0000000000 0.2420000000
     0.0000000000 0.5000000000 0.2420000000
     0.5000000000 0.0000000000 0.7420000000
     0.0000000000 0.5000000000 0.7420000000
     0.0000000000 0.0000000000 0.0000000000
     0.5000000000 0.5000000000 0.0000000000
     0.0000000000 0.0000000000 0.5000000000
     0.5000000000 0.5000000000 0.5000000000

Now, to populate this structure with hydrogen atoms, lets write a small script 
to add atoms to the C and N sites. We can see from the POSCAR that the C-N 
pairs are always oriented along the z-direction, so we will add 3 hydrogen
atoms "above" each C and "below" each N.::
    
    >>> n_h_bond = 1.01 #A
    >>> c_h_bond = 1.09 #A
    >>> 
    >>> s = io.read('POSCAR') # just reading in original structure
    >>> for atom in s:
            if atom.element.symbol == 'C':
                x = np.sin(np.pi/4)*c_h_bond
                x2 = np.sin(np.pi/4)*x
                ref = atom.cart_coord
                s.add_atom(Atom.create('H', s.get_coord(ref+[x,   0.0, x2])))
                s.add_atom(Atom.create('H', s.get_coord(ref+[-x2, -x2, x2])))
                s.add_atom(Atom.create('H', s.get_coord(ref+[-x2,  x2, x2])))
            elif atom.element.symbol == 'N':
                x = np.sin(np.pi/4)*c_h_bond
                x2 = np.sin(np.pi/4)*x
                # Note the angles of the N's attached hydrogens are rotated 
                # relative to the C's attached hydrogens.
                s.add_atom(Atom.create('H', s.get_coord(ref+[-x, 0.0, -x2])))
                s.add_atom(Atom.create('H', s.get_coord(ref+[x2,  x2, -x2])))
                s.add_atom(Atom.create('H', s.get_coord(ref+[x2, -x2, -x2])))

    >>> io.poscar.write(s, 'POSCAR_mod')

You can verify that the created structure has the right bond lengths::

    >>> s = io.read('POSCAR_mod')
    >>> for a1, a2 in itertools.combinations(s.atoms, r=2):
            d = s.get_distance(a1, a2)
            elts = set([ a1.element.symbol, a2.element.symbol ])
            if elts in [ set(['H', 'N']), set(['H', 'C']) ]:
                if d < 1.5:
                    print elts, d
    set([u'H', u'C']) 1.08999999999
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.08999999999
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.08999999999
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'C']) 1.08999999999
    set([u'H', u'C']) 1.09000000017
    set([u'H', u'N']) 1.00999999987
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999987
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999987
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999987
    set([u'H', u'N']) 1.00999999961
    set([u'H', u'N']) 1.00999999961

As you can see, all N-H and C-H bond lengths are correct.

Combinatorial site replacements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we have a good structure, lets start replacing atoms! First, we need
to specify the substitutions we will make. Lets start with simply isovalent
substitutions for Pb and I. In MePbI3, Methylammonium is a +1 ion, Pb is +2 and
I is -1. We will specify replacements in the form of lists of substitutions.::
    
    >>> pb_sub = [ 'Pb', 'Sn', 
                'Be', 'Mg', 'Ca', 'Sr', 'Ba',
                'V', 'Mn', 'Ni', 'Co', 'Fe', 'Zn',
                'Cd', 'Eu' ,'Ru', 'Pd', 'Pt', 'As']
    >>> i_sub = [ 'I', 'Br', 'Cl', 'F', 'H',
                'N', 'S' ]

Next, we need to create a directory structure that is reasonable for 
understanding where the structures are. This is primarily to make it easier 
for people to find the calculations by hand; qmpy would be find with randomly 
generated strings for folder names. We organize the structures into nested
directories of the form {anion}/{cation}. The substitutions are implemented by
the :func:`~qmpy.Structure.substitute` method.::
    
    >>> # first we write a little helper function for making folders
    >>> def mkdir(path):
            if not os.path.exists(path):
                os.mkdir(path)
    >>> # now we loop through antion/cation pairs and for each we:
    >>> #   create the POSCAR
    >>> #   create an Entry
    >>> project = Project.get('example')
    >>> for anion in i_sub:
            mkdir(anion)
            for cation in pb_sub:
                new_dir = '%s/%s' % (anion, cation)
                mkdir(new_dir)
                new_struct = s.replace({'Pb':cation,
                                        'I':anion})
                io.poscar.write(s, new_dir+'/POSCAR')
                entry = Entry.create(new_dir+'/POSCAR', projects=[project])
                entry.save()
                task = Task.create(entry, 'static')

Running the calculations
^^^^^^^^^^^^^^^^^^^^^^^^

In order to run calculations with qmpy, we utilize a JobManager and
TaskManager. The role of the TaskManager is to look at the calculations that
have been requested (in the form of Tasks), and will attempt to fill the
available resources with those calculations. The calculations are stored as
Jobs, which tracks where the calculation is being run, and where it came from.
This is where the JobManager takes over, checking all running Jobs, and if it
is found to be done, it is collected. These managers can be accessed through
the oqmd script (qmpy/bin/oqmd) either as a daemon process or, more safely, in
a screen.::

    $ oqmd jobserver -T run

and::

    $ oqmd taskserver -T run

As Tasks and Jobs are processed, both of these methods will continuously report
job submissions, task completions, as well as errors encountered.

Other examples
--------------

Now, we will run through a variety of problems, and demonstrate solutions which
leverage different functionalities with qmpy.

Identification of FCC decortations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, we will find all binary entries::

    >>> binaries = Entry.objects.filter(ntypes=2)
    >>> fcc = Composition.get('Cu').ground_state.structure

Then we run through every structure, and see if replacing all atoms with Cu
results in a structure that is equivalent (on volume scaling) with FCC Cu.::

    >>> fccs = []
    >>> for entry in binaries[:100]:
    >>>     struct = entry.structure
    >>>     ## Construct a dictionary of elt:replacement_elt pairs
    >>>     ## where every replacement is Cu
    >>>     rdict = dict((k, 'Cu') for k in entry.comp)
    >>>     test = struct.substitute(rdict, rescale=False,
    >>>                                     in_place=False)
    >>>     if fcc == test: # simple equality testing will work
    >>>         fccs.append(entry)


.. Warning::
    If you actually try to run this on the entire database, understand that it
    will take a pretty long time! Each entry tested takes between 0.1 and 1
    second, so it would take most of 24 hours to run through all 80,000+ binary 
    database entries.
    
Deviation from Vagard's Law
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the element_groups dictionary to look get a list of all simple metals::

    >>> elts = element_groups['simple-metals']

Then, for each pair of metals get all of the entries, and their volumes.::
    
    >>> vols = {}
    >>> for e1, e2 in itertools.combinations(elts, r=2):
    >>>     entries = Composition.get_list([e1, e2])
    >>>     for entry in entries:
    >>>         vol = entry.structure.volume_pa
    >>>         vols[entry.name] = vols.get(entry.name, []) + [vol]

Then, for every composition get the Vagard's law volume.::
    
    >>> vagards = {}
    >>> for comp in vols:
    >>>     comp = parse_comp(comp) # returns a elt:amt dictionary
    >>>     uc = unit_comp(comp) # reduces to a total of 1 atom
    >>>     vvol = 0
    >>>     for elt, amt in uc.items():
    >>>         vvol += elements[elt]['volume']*amt

More things you can do:
* Calculate an average error for each system
* Make a scatter plot for a few binaries show in volume vs x
* Look for cases where some are above and some are below
* Get relaxed volume of all stable compounds
* What about including the "nearly stable"

Compute all A-B bond lengths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This script loops over pairs of elements, gets the binary PhaseSpace, and then
loops over structures on the convex hull.::

    >>> for e1, e2 in itertools.combinations(elts, r=2):
    >>>     # do logic
    >>>     if e1 == e2:
    >>>         break
    >>>     ps = PhaseSpace([e1,e2])
    >>>     k = frozenset([e1,e2])
    >>>     bonds = []
    >>>     for p in ps.stable:
    >>>         s = p.calculation.input
    >>>         if s.ntypes < 2:
    >>>             continue
    >>>         dists = get_pair_distances(s, 10)
    >>>         bonds.append(min(dists[k]))
    >>>     print e1, e2, np.average(bonds), np.std(bonds)


Integrating with Sci-kit Learn
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, the necessary imports::

    >>> from sklearn.svm import SVR
    >>> from sklearn.ensemble import GradientBoostingRegressor
    >>> from sklearn import cross_validation
    >>> from sklearn.decomposition import PCA
    >>> from sklearn import linear_model
    >>> from sklearn import grid_search
    >>> from qmpy import *

As an example problem, we will build a very simple model that predicts the 
volume of a compound at a given composition based only on the composition::

    >>> elts = Element.objects.filter(symbol__in=element_groups['simple-metals'])
    >>> out_elts = Element.objects.exclude(symbol__in=element_groups['simple-metals'])
    >>> models = Calculation.objects.filter(path__contains='icsd')
    >>> models = models.filter(converged=True, label__in=['static', 'standard'])
    >>> models = models.exclude(composition__element_set=out_elts)
    >>> data = models.values_list('composition_id', 'output__volume_pa')

Now we will build a fit set and test set::

    >>> y = []
    >>> X = []
    >>> for c, v in data:
    >>>     y.append(v)
    >>>     X.append(get_basic_composition_descriptors(c).values())
    >>> X = np.array(X)
    >>> y = np.array(y)
    >>> x1, x2, y1, y2 = cross_validation.train_test_split(X, y, train_size=0.5)

Now to actually implement the model::

    >>> clf = linear_model.LinearRegression()
    >>> clf.fit(x1, y1)
    >>> clf.score(x2, y2)

More examples
-------------

For more examples check in qmpy/examples for a variety of scripts that
demonstrate these and other tasks. 

+------------------------------+----------------------------------------------+
| Script                       | Description                                  |
+==============================+==============================================+
| sklearn/build_model.py       | Build a volume model using sklearn to        |
|                              | predict structure volume based only on       |
|                              | composition.                                 |
+------------------------------+----------------------------------------------+
| structures/modify_CNPbI3.py  | Take an incomplete structure CNPbI3, that is |
|                              | supposed to be (CH3NH3)PbI3, and add missing |
|                              | H atoms.                                     |
+------------------------------+----------------------------------------------+
| structures/make_protos.py    | Take a base structure and create a variety   |
|                              | of decorations.                              |
+------------------------------+----------------------------------------------+
| structures/find_layered.py   | Search through the database of structures    |
|                              | for cases where the structure is not fully   |
|                              | connected, i.e. layered structures.          |
+------------------------------+----------------------------------------------+
| structures/bond_lengths.py   | Compute average A-B bond lengths for all A-B |
|                              | pairs, using all stable structures.          |
+------------------------------+----------------------------------------------+
| database/discovery_rate.py   | Using reference information from the ICSD    |
|                              | and measures of structural uniqueness find   |
|                              | the nominal year of `discovery' for all ICSD |
|                              | structures.                                  |
+------------------------------+----------------------------------------------+
| database/precipitates.py     | Screen for good precipitate strengtheners.   |
|                              | Creates the results used in <insert ref>     |
+------------------------------+----------------------------------------------+
| database/Li-M-O_screen.py    | Screen for (MO_x).(LiO_2) compounds for      |
|                              | hybrid Li-ion/Li-O2 electrode materials.     |
|                              | Reproduces the results used in <insert ref>. |
+------------------------------+----------------------------------------------+
| database/oqmd_vs_expt.py     | Compare OQMD formation energies with         |
|                              | experimental formation energies.             |
+------------------------------+----------------------------------------------+
| analysis/chem_pots.py        | Plot of all modified chemical potentials.    |
+------------------------------+----------------------------------------------+
| analysis/pot_fitting.py      | Fit chemical potentials.                     |
+------------------------------+----------------------------------------------+
| analysis/get_formations.py   | Calculation formation energies based on new  |
|                              | chemical potentials.                         |
+------------------------------+----------------------------------------------+
