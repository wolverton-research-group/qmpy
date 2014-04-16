# qmpy/analysis/symmetry/spacegroup.py

import os
import fractions as frac
import numpy as np
import logging

from django.db import models

import qmpy.utils as utils
from routines import *

logger = logging.getLogger(__name__)

class TranslationError(Exception):
    pass

class RotationError(Exception):
    pass

class OperationError(Exception):
    pass

class WyckoffSiteError(Exception):
    pass

class SpacegroupError(Exception):
    pass

class Translation(models.Model):
    """
    A translation operation.

    Relationships:
        | :mod:`~qmpy.Spacegroup` via spacegroup
        | :mod:`~qmpy.Operation` via operation

    Attributes:
        | id
        | x, y, z: Translation vector. Accessed via `vector`.

    Examples::
        
        >>> op = Operation.get('x', 'x+y', 'z-x+1/2')
        >>> print op.translsation
        <Translation: 0,0,+1/2>
        >>> print op.translation.vector
        array([ 0. ,  0. ,  0.5])

    """
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    class Meta:
        app_label = 'qmpy'
        db_table = 'translations'

    @property
    def vector(self):
        return np.array([self.x, self.y, self.z])

    @vector.setter
    def vector(self, vector):
        self.x, self.y, self.z = vector

    @classmethod
    def get(cls, vector):
        fields = ['x', 'y', 'z']
        arr_dict = dict(zip(fields, vector))
        obj, new = cls.objects.get_or_create(**arr_dict)
        if new:
            obj.save()
        return obj

    def __str__(self):
        ops = []
        for t in self.vector:
            if t == 0:
                s = '0'
            elif t < 0:
                s = '%s' % (frac.Fraction(str(t)))
            else:
                s = '+%s' % (frac.Fraction(str(t)))
            ops.append(s)
        return ','.join(ops)

class Rotation(models.Model):
    """
    A rotation operation.

    Relationships:
        | :mod:`~qmpy.Spacegroup` via spacegroup
        | :mod:`~qmpy.Operation` via operation

    Attributes:
        | id
        | a11, a12, a13
        | a21, a22, a23
        | a31, a32, a33: Rotation matrix. Accessed via `matrix`.

    Examples::

        >>> op = Operation.get('x', 'x+y', 'z-x+1/2')
        >>> print op.rotation
        <Rotation: x,x+y,-x+z>
        >>> print op.rotation.matrix
        array([[ 1.,  0.,  0.],
               [ 1.,  1.,  0.],
               [-1.,  0.,  1.]])


    """
    a11 = models.FloatField()
    a12 = models.FloatField()
    a13 = models.FloatField()
    a21 = models.FloatField()
    a22 = models.FloatField()
    a23 = models.FloatField()
    a31 = models.FloatField()
    a32 = models.FloatField()
    a33 = models.FloatField()

    class Meta:
        app_label = 'qmpy'
        db_table = 'rotations'

    @property 
    def matrix(self):
        return np.array([ 
            [ self.a11, self.a12, self.a13 ],
            [ self.a21, self.a22, self.a23 ],
            [ self.a31, self.a32, self.a33 ]])

    @matrix.setter
    def matrix(self, matrix):
        self.a11, self.a12, self.a13 = matrix[0]
        self.a21, self.a22, self.a23 = matrix[1]
        self.a31, self.a32, self.a33 = matrix[2]

    @classmethod
    def get(cls, matrix):
        fields = [ 'a11', 'a12', 'a13',
                   'a21', 'a22', 'a23',
                   'a31', 'a32', 'a33']
        matrix = np.ravel(matrix)
        mat_dict = dict(zip(fields, matrix))
        obj, new = cls.objects.get_or_create(**mat_dict)
        if new:
            obj.save()
        return obj

    def __str__(self):
        ops = []
        indict = {0:'x', 1:'y', 2:'z'}
        for r in self.matrix:
            s = ''
            for i, x in enumerate(r):
                if x == 0:
                    continue
                elif x == 1:
                    s += '+'+indict[i]
                elif x == -1:
                    s += '-'+indict[i]
                else:
                    f = frac.Fraction(str(x))
                    s += '%s%s' % (f, indict[i])
            ops.append(s)
        return ','.join(ops)

class Operation(models.Model):
    """ A symmetry operation (rotation + translation).

    Relationships:
        | :mod:`~qmpy.Spacegroup` via spacegroup
        | :mod:`~qmpy.Rotation` via rotation_set
        | :mod:`~qmpy.Translation` via translation_set

    Attributes:
        | id

    Examples::
        
        >>> op = Operation.get('x+y-1/2,-z-y+1/2,x-z+1/2')
        >>> print op
        <Operation: +x+y+1/2,-y-z+1/2,+x-z+1/2>

    """
    rotation = models.ForeignKey('Rotation')
    translation = models.ForeignKey('Translation')

    class Meta:
        app_label = 'qmpy'
        db_table = 'operations'

    @classmethod
    def get(cls, value):
        """
        Accepts symmetry operation strings, i.e. "+x, x+1/2, x+y-z" or a tuple
        of rotation matrix and translation vector. 

        Example::

            >>> Operation.get("x,y,-y")
            >>> Operation.get(( rot, trans ))

        """
        if isinstance(value, basestring):
            rot, trans = parse_sitesym(value)
        elif isinstance(value, tuple):
            rot, trans = value
        rot = Rotation.get(rot)
        trans = Translation.get(trans)
        op, new = cls.objects.get_or_create(rotation=rot, translation=trans)
        if new:
            op.save()
        return op

    def __str__(self):
        ops = []
        indict = {0:'x', 1:'y', 2:'z'}
        for r,t in zip(self.rotation.matrix, 
                       self.translation.vector):

            s = ''
            for i, x in enumerate(r):
                if x == 0:
                    continue
                elif x == 1:
                    s += '+'+indict[i]
                elif x == -1:
                    s += '-'+indict[i]
                else:
                    f = frac.Fraction(str(x)).limit_denominator(1000)
                    s += '%s%s' % (f, indict[i])

            if t == 0:
                pass
            elif t < 0:
                s += '-%s' % (frac.Fraction('%08f' % t))
            else:
                s += '+%s' % (frac.Fraction('%08f' % t))
            ops.append(s)
        return ','.join(ops)


class WyckoffSite(models.Model):
    """
    Base class for a Wyckoff site. (e.g. a "b" site).

    Relationships:
        | :mod:`~qmpy.Spacegroup` via spacegroup
        | :mod:`~qmpy.Atom` via atom_set
        | :mod:`~qmpy.Site` via site_set

    Attributes:
        | id
        | symbol: Site symbol
        | multiplicity: Site multiplicity
        | x, y, z: Coordinate symbols.

    """
    spacegroup = models.ForeignKey('Spacegroup', related_name='site_set')
    symbol = models.CharField(max_length=1)
    multiplicity = models.IntegerField(blank=True, null=True)
    x = models.CharField(max_length=8)
    y = models.CharField(max_length=8)
    z = models.CharField(max_length=8)
    
    class Meta:
        app_label = 'qmpy'
        db_table = 'wyckoffsites'

    def __str__(self):
        return '%s%d' % (self.symbol, self.multiplicity)

    @classmethod
    def get(cls, symbol, spacegroup):
        site, new = cls.objects.get_or_create(spacegroup=spacegroup, 
                symbol=symbol)
        if new:
            site.save()
        return site

class Spacegroup(models.Model):
    """
    Base class for a space group.

    Relationships:
        | :mod:`~qmpy.Structure` via structure_set
        | :mod:`~qmpy.Translation` via centering_vectors
        | :mod:`~qmpy.Operation` via operations
        | :mod:`~qmpy.WyckoffSite` via site_set

    Attributes:
        | number: Spacegroup #. (primary key)
        | centrosymmetric: (bool) Is the spacegroup centrosymmetric.
        | hall: Hall symbol.
        | hm: Hermann-Mauguin symobl.
        | lattice_system: Cubic, Hexagonal, Tetragonal, Orthorhombic,
        |   Monoclinic or Triclinic.
        | pearson: Pearson symbol
        | schoenflies: Schoenflies symbol.

    """
    number = models.IntegerField(primary_key=True)
    hm = models.CharField(max_length=30, blank=True, null=True)
    hall = models.CharField(max_length=30, blank=True, null=True)
    pearson = models.CharField(max_length=30)
    schoenflies = models.CharField(max_length=30)
    operations = models.ManyToManyField(Operation, null=True)
    centering_vectors = models.ManyToManyField(Translation)
    lattice_system = models.CharField(max_length=20)
    centrosymmetric = models.BooleanField(default=False)

    _sym_ops = None
    _rots = None
    _trans = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'spacegroups'

    def save(self, *args, **kwargs):
        super(Spacegroup, self).save(*args, **kwargs)
        for op in self.sym_ops:
            op.save()
        self.operations = self.sym_ops

    @staticmethod
    def get(number):
        return Spacegroup.objects.get(number=number)

    @property
    def sym_ops(self):
        """List of (rotation, translation) pairs for the spacegroup"""
        if self._sym_ops is None:
            self._sym_ops = [ op for op in self.operations.all() ]
        return self._sym_ops

    @sym_ops.setter
    def sym_ops(self, sym_ops):
        self._sym_ops = sym_ops

    @property
    def rotations(self):
        """List of rotation operations for the spacegroup."""
        if self._rots is None:
            self._rots = np.array([ op.rotation.matrix for op in self.sym_ops ])
        return self._rots

    @property
    def translations(self):
        """List of translation operations for the spacegroup."""
        if self._trans is None:
            self._trans = np.array([ op.translation.vector for op in self.sym_ops ])
        return self._trans

    def __str__(self):
        return str(self.number)

    @property
    def wyckoff_sites(self):
        """List of WyckoffSites."""
        return self.site_set.all().order_by('symbol')

    @property
    def symbol(self):
        """Returns the Hermann-Mauguin symbol for the spacegroup"""
        return self.hm

    def equivalent_sites(self, point, tol=1e-3):
        equiv = []
        for rot, trans in zip(self.rotations, self.translations):
            new = utils.wrap(np.dot(rot, point) + trans)
            if not any([ all([ abs(o-n) < tol for o,n in zip(old, new)])
                                              for old in equiv]):
                equiv.append(new)
        return equiv

    @property
    def n_sym_ops(self):
        return self.operations.count()

    @property
    def n_wyckoff_sites(self):
        return self.site_set.count()

    def get_site(self, symbol):
        """Gets WyckoffSite by symbol."""
        symol = symbol.strip('0123456789')
        return self.site_set.get(symbol__exact=symbol)
