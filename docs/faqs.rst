====
FAQs
====

1. Where are the input structures for compounds in the ICSD?

    Because we have an agreement with the ICSD, we are unable to provide the original structures. 
    We provide the ICSD collection code instead, so that anyone with access to the ICSD can 
    obtain the original structures.

2. Where are the references for the experimental formation energy values?

    These values were collected from multiple sources as detailed in this paper:
    `npj Comput. Mater. 1, 15010 (2015)`_. 
    Specific source for an individual experimental formation energy value may be obtained 
    from a locally hosted QMDB database by querying for ``qmpy.ExptFormationEnergy`` objects
    of the composition of interest.
    
3. I am encountering problems with pip installation of the new qmpy release (v1.3.0). What to do?
    
    - Some packages qmpy *depends on* may not play nice with pip. If you encounter errors
      related to other packages while installing qmpy (usual suspects are ``scipy``, ``numpy``,
      ``MySQL-python``, ``matplotlib``, ``pygraphviz``), try installing
      the "problem package" using conda instead, and then re-attempt to install qmpy. In the
      appropriate environment, do (using ``pygraphviz`` as an example):
    
        $ conda install pygraphviz 
    
    - Import of ``matplotlib.cbook`` is enforced in ``qmpy`` v1.3.0 which may require the 
      user to install/update the python package ``six`` in their python environment. 
      We might be removing this indirect dependency in the future updates. 
      But for now, the ``six`` package may be installed by:
    
        $ pip install six

.. _`npj Comput. Mater. 1, 15010 (2015)`: http://dx.doi.org/10.1038/npjcompumats.2015.10
