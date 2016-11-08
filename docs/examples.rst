========
Examples
========

To be filled out in more detail

Identification of FCC decortations
----------------------------------

First, we will find all binary entries::

    >>> binaries = Entry.objects.filter(ntypes=2)
    >>> fcc = Composition.get('Cu').ground_state.structure

Then we run through every structure, and see if replacing all atoms with Cu
results in a structure that is equivalent (on volume scaling) with FCC Cu.::

    >>> fccs = []
    >>> for entry in binaries[:100]:
    >>>     struct = entry.structure
    >>>     ## Construct a dictionary of elt:replacement_elt pairs
    >>>     ## where every replacement is Cu
    >>>     rdict = dict((k, 'Cu') for k in entry.comp)
    >>>     test = struct.substitute(rdict, rescale=False,
    >>>                                     in_place=False)
    >>>     if fcc == test: # simple equality testing will work
    >>>         fccs.append(entry)


.. Warning::
    If you actually try to run this on the entire database, understand that it
    will take a pretty long time! Each entry tested takes between 0.1 and 1
    second, so it would take most of 24 hours to run through all 80,000+ binary 
    database entries.
    
Deviation from Vagard's Law
---------------------------


Use the element_groups dictionary to look get a list of all simple metals::

    >>> elts = element_groups['simple-metals']

Then, for each pair of metals get all of the entries, and their volumes.::
    
    >>> vols = {}
    >>> for e1, e2 in itertools.combinations(elts, r=2):
    >>>     entries = Composition.get_list([e1, e2])
    >>>     for entry in entries:
    >>>         vol = entry.structure.volume_pa
    >>>         vols[entry.name] = vols.get(entry.name, []) + [vol]

Then, for every composition get the Vagard's law volume.::
    
    >>> vagards = {}
    >>> for comp in vols:
    >>>     comp = parse_comp(comp) # returns a elt:amt dictionary
    >>>     uc = unit_comp(comp) # reduces to a total of 1 atom
    >>>     vvol = 0
    >>>     for elt, amt in uc.items():
    >>>         vvol += elements[elt]['volume']*amt

Addendum:
* Calculate an average error for each system
* Make a scatter plot for a few binaries show in volume vs x
* Look for cases where some are above and some are below
* Get relaxed volume of all stable compounds
* What about including the "nearly stable"
