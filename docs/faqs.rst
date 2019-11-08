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
      We will be removing this indirect dependency in the future updates. 
      But for now, the ``six`` package may be installed by:
    
        $ pip install six
        
    - Right out of the box, the new version of ``qmpy`` supports only the latest ``qmdb`` SQl 
      database that we've released along with it. This constraint arises due to a 
      change in SQL schema, which added an extra column, ``element_list``, in one of the
      SQL relations (data tables). So we **strongly recommend** using the updated database with 
      ``qmpy`` v1.3.0. But if you still prefer to use one of the older ``qmdb`` 
      versions which was already installed in your system, the suggested workaround is to 
      create a new column on the ``Composition`` table named ``element_list`` through SQL
      commands and then fill in those table columns with values using qmpy API. The value 
      ``element_list`` is defined `here <https://github.com/wolverton-research-group/qmpy/blob/eb592d7846676b8c40399190235575959eb4983b/qmpy/materials/composition.py#L96>`_ as:
      
          ``comp.element_list = '_'.join(comp.comp.keys())+'_'``
      

.. _`npj Comput. Mater. 1, 15010 (2015)`: http://dx.doi.org/10.1038/npjcompumats.2015.10
