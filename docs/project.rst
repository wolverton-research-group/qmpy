==========================================================
Using qmpy to manage a high-throughput calculation project
==========================================================

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
----------------------------------

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
    spinels:
      allocations: [bigcluster]
      priority: 0
      users: [oqmdrunner]
    
We title the project "spinels", since that will be our example project, and
define the lists of allocations that this project is authorized to use, and the
users that are associated with the project. In order to apply these changes,
run::
    
    >>> from qmpy import *
    >>> sync_resources()


Combinatorial site replacements
-------------------------------

If, for example, we say that we want to calculate i) a range of defects in a
host matrix or ii) a wide range of compositions in a particular structure. It
is possible to do this in the framework of qmpy, with minimal effort. 

