====
FAQs
====

1. Where are the input structures?

    Because we have an agreement with the ICSD, we are unable to provide the original structures. 
    We provide the ICSD collection code number instead, so that anyone with access to the ICSD can 
    obtain the original structure.

2. Where are the references for the experimental formation energy values?

    These values were collected from multiple sources as detailed here in [Kirklin2015]_. 
    Specific source for an individual experimental formation energy value may be obtained 
    from a locally hosted qmdb-SQL-database by querying for "qmpy.ExptFormationEnergy" objects
    
3. I am encountering problems with pip installation of the new qmpy(v1.3.0). What to do?

    - Installation of the dependency package pygraphviz via pip could raise issues in 
      some systems. If you're using a conda environment, it maybe easily solved by 
      installing pygraphviz prior to the qmpy installation via
    
        $ conda install pygraphviz 
    
    - Import of matplotlib.cbook is enforced in qmpy v1.3.0 which may require the 
      user to install/update the python package "six" in their python environment. 
      We might be removing this indirect dependency in the future updates. 
      But for now, the "six" package may be installed by
    
        $ pip install six

.. [Kirklin2015] Kirklin, Scott, et al. "The Open Quantum Materials Database (OQMD): assessing the accuracy of DFT formation energies." npj Computational Materials 1 (2015): 15010.
