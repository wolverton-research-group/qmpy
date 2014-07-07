Calculations
------------

.. module:: qmpy

In :mod:`qmpy` a VASP calculation is represented by a :mod:`~qmpy.Calculation`
object. This object contains tools for writing calcualtion inputs and reading
calculation outputs. Additionally, it provides tools for automatically
correcting errors in calculations. 

Calculation
^^^^^^^^^^^
.. autoclass:: qmpy.Calculation
  :members:

Density of States
^^^^^^^^^^^^^^^^^

.. autoclass:: qmpy.DOS
  :members:

Potential
^^^^^^^^^
.. autoclass:: qmpy.Potential
  :members:

.. autoclass:: qmpy.Hubbard
  :members:
