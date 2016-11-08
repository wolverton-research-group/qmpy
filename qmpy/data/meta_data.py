#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
import logging

logger = logging.getLogger(__name__)

class MetaData(models.Model):
    """
    Base class for variable typed model tagging.

    Model for arbitrary meta-data descriptors for various qmpy objects.
    Generally accessed by properties and methods added by the "add_label"
    descriptor. See "add_label" for a more detailed description of its use

    Relationships
        | :mod:`~qmpy.Calculation` via calculation_set
        | :mod:`~qmpy.Composition` via composition_set
        | :mod:`~qmpy.DOS` via dos_set
        | :mod:`~qmpy.Entry` via entry_set
        | :mod:`~qmpy.Structure` via structure_set

    Attributes:
        | id: Autoincrementing primary key
        | type: Label for the kind of meta data, e.g. "hold", "keyword" 
        | value: Content of the meta data. e.g. "repeated failure", "known 
        |   anti-ferromagnetic"

    Examples::

        >>> MetaData.get('Keyword', 'ICSD')
        <Keyword: ICSD>
    """
    type = models.CharField(max_length=15)
    value = models.TextField()

    class Meta:
        app_label = 'qmpy'
        db_table = 'meta_data'

    def __str__(self):
        return self.value

    def __repr__(self):
        return '<%s: %s>' % (self.type.title(), self.value)

    @classmethod
    def get(cls, type, value):
        md, new = MetaData.objects.get_or_create(type=type, value=value)
        if new:
            md.save()
        return md

class GlobalWarning(object):
    @staticmethod
    def set(warning):
        md = MetaData.get('global_warning', warning)
        md.save()
        return md

    @staticmethod
    def clear(warning):
        md = MetaData.get('global_warning', warning)
        md.delete()

    @staticmethod
    def list():
        return list(MetaData.objects.filter(type='global_warning'))

class GlobalInfo(object):
    @staticmethod
    def set(warning):
        md = MetaData.get('global_info', warning)
        md.save()
        return md

    @staticmethod
    def clear(warning):
        md = MetaData.get('global_info', warning)
        md.delete()

    @staticmethod
    def list():
        return list(MetaData.objects.filter(type='global_info'))

class DatabaseUpdate(object):
    @staticmethod
    def value():
        return MetaData.objects.get(type='database_update').value

    @staticmethod
    def set():
        MetaData.objects.filter(type='database_update').update(
                value=str(datetime.date(datetime.now())))

def add_meta_data(label, plural=None, cache=None, description=''):
    """
    Decorator for adding managed attributes for MetaData types to other models.

    Requires that the class being decorated has a many_to_many field with
    MetaData.

    Example::

        >>> @add_label("keywords")
        >>> class NewModel(models.Model):
        >>>     meta_data = models.ManyToManyField('MetaData')
        >>> 
        >>> instance = NewModel()
        >>> instance.keywords
        []
        >>> instance.add_keyword('decorated!')
        >>> instance.keywords
        [<Keyword: decorated!>]
        >>> instance.remove_keyword('decorated!')
        >>> instance.keywords
        []
        >>> instance.keywords = ['add', 'in', 'bulk']
        >>> instance.keywords
        [<Keyword: add>, <Keyword: in>, <Keyword: bulk>]

    """
    if plural is None:
        plural = '%ss' % label
    if cache is None:
        cache = '_%s' % plural
    label = label.lower()
    plural = plural.lower()
    cache = cache.lower()

    def func(cls):
        setattr(cls, cache, None)
        def getter(self):
            if getattr(self, cache) is None:
                if getattr(self, 'pk') is None:
                    setattr(self, cache, [])
                else:
                    data = self.meta_data.filter(type=label)
                    data = data.values_list('value', flat=True)
                    setattr(self, cache, list(data))
            return getattr(self, cache)

        def setter(cls, values):
            setattr(cls, cache, values)

        setattr(cls, plural, property(getter, 
                                     setter, 
                                     None, 
                                     description))
        def adder(cls, value):
            'Helper function to add %s to list of %s.' % (label, plural)
            existing = getattr(cls, plural)
            if not value in existing:
                existing.append(value)
        setattr(cls, 'add_%s' % label, adder)

        def remover(cls, value):
            'Helper function to remove a %s from list of %s.' % (label, plural)
            existing = getattr(cls, plural)
            if value in existing:
                existing.remove(value)
        setattr(cls, 'remove_%s' % label, remover)

        doc = 'Return list of %s (MetaData objects of type %s)' % (plural,
                label)
        def obj_getter(self):
            return [ MetaData.get(label, v) for v in getattr(self, plural) ]
        setattr(cls, '%s_objects' % label, property(obj_getter, None, None, doc))

        return cls
    return func
