import qmpy
import qmpy.data as data

import logging

logger = logging.getLogger(__name__)

def apply_filter(words, keyword):
    """
    Assign a keyword to all entries whose references contain any of the given
    list of words.

    Examples:
    >>> apply_filter(["pressure", "mpa", "gpa", "kbar"], "high pressure")
    """
    entries = qmpy.Entry.objects.none()
    for word in words:
        entries |= qmpy.Entry.objects.filter(title__contains=word)
    kw = qmpy.MetaData.get('keyword', keyword)
    kw.entry_set.add(*entries)

def is_likely_high_pressure(structure):
    pressure_words = [
            'pressure',
            'anvil cell',
            'dac',
            'mpa', 'gpa',
            'mbar', 'kbar']

    # add test for volume deviation from vagards law

    if structure.pressure > 102:
        return True
    if structure.reference:
        if structure.reference.title:
            title = structure.reference.title.lower()
            for w in pressure_words:
                if w in title:
                    return True
    return False
