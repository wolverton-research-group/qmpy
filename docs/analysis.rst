**************
Analysis tools
**************

Basically all thermodynamic analysis in qmpy is done starting from a
:mod:`~qmpy.PhaseSpace` instance. If you have the database install and working,
these are very easy to construct::

    >>> ps = PhaseSpace('Li-Si')
    >>> ps
    <PhaseSpace bound by Li-Si>

Since the PhaseSpace was created without any extra arguments, it was assumed
that you wanted to pull thermodynamic data from the OQMD, but you can fine tune
the data that is included very easily. More on that later.

Convex Hull Construction
------------------------

To obtain the convex hull for any phase space, simply access the `hull`
attribute::

    >>> ps.hull
    set([<Equilibrium: Li13Si4-Li21Si5>, <Equilibrium: Li12Si7-Li7Si3>,
    <Equilibrium: Li13Si4-Li7Si3>, <Equilibrium: LiSi-Li12Si7>, <Equilibrium:
    Li21Si5-Li>, <Equilibrium: LiSi-Si>])

The hull is a set of Equilibrium objects, which have very natural attributes::

    >>> eq = list(ps.hull)[0]
    >>> eq.phases
    [<Phase Li13Si4 : -0.240>, <Phase Li21Si5 : -0.212>]
    >>> eq.chem_pots
    {u'Si': -0.74005684434211016, u'Li': -0.086299552894736051}

Phase Stability
---------------

Positive for unstable phases, negative for stable phases.

Examples::

    >>> p = ps.phase_dict['Li13Si4'] # for just one phase
    >>> ps.compute_stability(p)
    >>> p.stability
    -0.007333029175317474
    >>> ps.compute_stabilities()
    >>> ps.phase_dict['Li2Si'].stability
    0.03116726059829092

Grand Canonical Linear Programming
----------------------------------

Examples::

    >>> energy, phases = ps.gclp('LiSi2')
    >>> energy
    -0.404968066250002
    >>> phases
    {<Phase LiSi : -0.202>: 2.0, <Phase Si : 0>: 1.0}
    >>> energy, phases = ps.gclp('Si', mus={'Li':-0.4})
    >>> phases
    {<Phase LiSi : -0.202>: 2.0}


Convex Hull Slices
------------------

Works by recursively using linear programming to find the lowest point
contained within the a specified compositional region.

Examples::

    >>> ps = PhaseSpace('Fe2O3-Li2O')
    >>> ps.hull
    set([<Equilibrium: LiFe5O8-LiFeO2>, <Equilibrium:
    LiFeO2-Li5FeO4>, <Equilibrium: LiFe5O8-Fe2O3>, <Equilibrium:
    Li5FeO4-Li2O>])

Reaction Enumeration
--------------------

Stability Conditions
--------------------

