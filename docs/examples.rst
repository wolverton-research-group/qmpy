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

Compute all A-B bond lengths
----------------------------

This script loops over pairs of elements, gets the binary PhaseSpace, and then
loops over structures on the convex hull.::

    >>> for e1, e2 in itertools.combinations(elts, r=2):
    >>>     # do logic
    >>>     if e1 == e2:
    >>>         break
    >>>     ps = PhaseSpace([e1,e2])
    >>>     k = frozenset([e1,e2])
    >>>     bonds = []
    >>>     for p in ps.stable:
    >>>         s = p.calculation.input
    >>>         if s.ntypes < 2:
    >>>             continue
    >>>         dists = get_pair_distances(s, 10)
    >>>         bonds.append(min(dists[k]))
    >>>     print e1, e2, np.average(bonds), np.std(bonds)


Integrating with Sci-kit Learn
------------------------------

First, the necessary imports::

    >>> from sklearn.svm import SVR
    >>> from sklearn.ensemble import GradientBoostingRegressor
    >>> from sklearn import cross_validation
    >>> from sklearn.decomposition import PCA
    >>> from sklearn import linear_model
    >>> from sklearn import grid_search
    >>> from qmpy import *

As an example problem, we will build a very simple model that predicts the 
volume of a compound at a given composition based only on the composition::

    >>> elts = Element.objects.filter(symbol__in=element_groups['simple-metals'])
    >>> out_elts = Element.objects.exclude(symbol__in=element_groups['simple-metals'])
    >>> models = Calculation.objects.filter(path__contains='icsd')
    >>> models = models.filter(converged=True, label__in=['static', 'standard'])
    >>> models = models.exclude(composition__element_set=out_elts)
    >>> data = models.values_list('composition_id', 'output__volume_pa')

Now we will build a fit set and test set::

    >>> y = []
    >>> X = []
    >>> for c, v in data:
    >>>     y.append(v)
    >>>     X.append(get_basic_composition_descriptors(c).values())
    >>> X = np.array(X)
    >>> y = np.array(y)
    >>> x1, x2, y1, y2 = cross_validation.train_test_split(X, y, train_size=0.5)

Now to actually implement the model::

    >>> clf = linear_model.LinearRegression()
    >>> clf.fit(x1, y1)
    >>> clf.score(x2, y2)
