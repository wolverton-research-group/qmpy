#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
import json
import logging

from qmpy.utils import *

logger = logging.getLogger(__name__)

class Author(models.Model):
    """
    Base class for an author.

    Relationships:
        | :mod:`~qmpy.Reference` via references

    Database Fields:
        | id
        | first
        | last

    """
    last = models.CharField(max_length=30, blank=True, null=True)
    first = models.CharField(max_length=30, blank=True, null=True)
    class Meta:
        app_label = 'qmpy'
        db_table = 'authors'

    @property
    def name(self):
        return self.proper_last+', '+self.proper_first

    @property
    def proper_last(self):
        if not self.last:
            return None
        elif len(self.last) == 1:
            return self.last.upper()
        else:
            return self.last[0].upper()+self.last[1:]

    @property
    def proper_first(self):
        if not self.first:
            return None
        elif len(self.first.split()) == 1:
            if len(self.first) == 1:
                return self.first[0].upper()+'.'
            else:
                return self.first[0].upper()+self.first[1:]
        else:
            return ' '.join(l[0].upper()+"." for l in self.first.split())

    def __str__(self):
        if self.first and self.last:
            return '%s, %s' % (self.proper_last, self.proper_first)
        elif self.first and not self.last:
            return self.proper_first
        elif self.last and not self.first:
            return self.proper_last

    @classmethod
    def from_name(cls, name):
        commas = name.count(',')
        spaces = name.count(' ')
        if commas == 1:
            last, first = name.split(',')
        elif commas == 0 and spaces:
            first = name.split()[0]
            last = ' '.join(name.split()[1:])
        else:
            last = name.split(',')[0]
            first = ' '.join(name.split(',')[1:])
        author, new = Author.objects.get_or_create(
                last=last.lower().strip(), first=first.lower().strip())
        return author

class Journal(models.Model):
    """
    Base class for a journal

    Relationships:
        | :mod:`~qmpy.Reference` via references

    Database fields: 
        | id
        | name
        | code
    """
    code = models.CharField(max_length=10, unique=True, null=True)
    name = models.TextField(null=True)
    class Meta:
        app_label = 'qmpy'
        db_table = 'journals'

    def __str__(self):
        if self.name:
            return self.name
        elif self.code:
            return self.code

class Reference(models.Model):
    """
    Base class for a reference to a publication.

    Relatioships:
        | :mod:`~qmpy.Author` via author_set
        | :mod:`~qmpy.Journal` via journal
        | :mod:`~qmpy.Entry` via entry_set
        | :mod:`~qmpy.Structure` via structure_set

    Database fields: 
        | id
        | title
        | year
        | volume
        | page_first
        | page_last

    """
    author_set = models.ManyToManyField(Author, related_name='references',
            null=True)
    journal = models.ForeignKey(Journal, related_name='references', 
            null=True)
    title = models.TextField(null=True)
    volume = models.IntegerField(null=True)
    page_first = models.IntegerField(null=True)
    page_last = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)

    _authors = []
    class Meta:
        app_label = 'qmpy'
        db_table = 'publications'

    def save(self,*args, **kwargs):
        if self.journal:
            self.journal.save()
        super(Reference, self).save(*args, **kwargs)
        self.author_set = self._authors

    @property
    def authors(self):
        if not self._authors:
            self._authors = list(self.author_set.all())
        return self._authors

    @authors.setter
    def authors(self, authors):
        self._authors = authors

    def __str__(self):
        s = self.title
        if self.authors:
            s += ': %s' % self.authors[0]
        if self.journal is not None:
            s += ': %s' % self.journal
        return s

    @property
    def citation(self):
        retval = ', '.join(str(a) for a in self.authors)
        if self.year:
            retval += '('+str(self.year)+')'
        if self.title:
            retval += '. '+self.title.strip().rstrip('.')
        if self.journal:
            retval += '. '+str(self.journal)
            if self.volume:
                retval += ', '+str(self.volume)
                if self.page_first:
                    retval += ', '+str(self.page_first)
                    if self.page_last:
                        retval += '-'+str(self.page_last)
        return retval+'.'

