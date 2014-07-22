#!/usr/bin/env python

import numpy as np
cimport numpy as np
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

import numpy.linalg as linalg
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

def find_nearest_neighbors(structure, method='closest', limit=5, tol=2e-1,
        **kwargs):
    """
    For each atom in the `structure` assign the nearest neighbors.

    Keyword Arguments:
        method ('closest' or 'voronoi'):
            closest: 
                Atoms A and B are neighbors, if and only if there is no atom C 
                such that AC < AB and BC < AB. Once all pairs of this kind 
                have been assigned, the nearest neighbors are those within 
                `tol` of the shortest distance.

            voronoi: 
                Assign nearest neighbors based on voronoi construction.
                For each atom which generates a voronoi facet, `tol` specifies
                the minimum area of the facet before the atom is considered a
                nearest neighbor.

            defaults to 'closest'

        limit:
            Range outside of the unit cell that will be searched for nearest
            neighbor atoms.

        tol: Varied depending on the method being used.

    Returns:
        dict of Atom:list of Atom pairs. For each atom in the structure, its
        "neighbors" attribute will be set to the list of its nearest neighbors.

    .. Note:: Recommended to use the "closest" method unless you are sure you
              what the "voronoi" method will do. The voronoi neighbors are
              useful for some purposes, but are often not what are normally
              considered nearest neighbors. For example in BCC the second
              nearsest neighbors contribute to facets in the an atoms voronoi
              cell. The tolerance specification for this method sets the
              minimum area of such a facet required to add the atom as a
              nearest neighbor. In the BCC case, this cutoff must be set to at
              least 2.3 A^2 to exclude the facets due to second nearest
              neighbors.

    """

    if method == 'closest':
        return _heuristic(structure, tol=tol, limit=limit)
    elif method == 'voronoi':
        return _voronoi(structure, tol=tol, limit=limit)
    else:
        raise ValueError("keyword 'method' must be 'closest' or 'voronoi'")

def _get_facet_area(vertices):
    area = 0
    vertices = vertices[np.lexsort(vertices.T)]
    if not vertices.shape[1] == 3:
        raise ValueError('vertices must be an Nx3 array')
    for i in range(len(vertices)-2):
        a = vertices[i]
        b = vertices[i+1]
        c = vertices[i+2]
        ab = b-a
        ac = c-a
        area += linalg.norm(np.cross(ab, ac))
    return area

def _heuristic(structure, limit=5, tol=2e-1):
    lat_params = structure.lat_params

    # Create a new cell large enough to find neighbors at least `limit` away.
    limits = [ int(np.ceil(limit/lat_params[i])) for i in range(3) ]
    new_struct = structure.transform(limits, in_place=False)

    # construct a distance matrix between the original structure and supercell
    # structure.
    distances = np.zeros((len(structure.sites), 
                          structure.natoms*np.product(limits)))
    for i, site in enumerate(structure.sites):
        for j, atom in enumerate(new_struct.sites):
            dist = new_struct.get_distance(i, j, limit=limit, wrap_self=True)
            if dist is None or dist < 1e-4:
                dist = min(structure.lat_params[:3])
            distances[i,j] = dist

    nns = {}
    for i, a in enumerate(structure.sites):
        a.neighbors = []
        dists = np.array(distances[i])
        dists /= min([d for d in dists ])
        # get neighbors within `tol` % of the shortest bond length
        inds = np.ravel(np.argwhere((dists - 1) < tol))
        inds = np.array([ ii for ii in inds if ii != i ])
        # map index back into the original cell
        inds %= structure.natoms
        a.neighbors = [ structure.sites[j] for j in inds ]
        nns[a] = a.neighbors
    #return nns

def _voronoi(structure, limit=5, tol=1e-2):
    lps = structure.lat_params
    limits = np.array([ int(np.ceil(limit/lps[i])) for i in range(3)])

    # Create a new cell large enough to find neighbors at least `limit` away.
    new_struct = structure.transform(limits+1, in_place=False)
    nns = defaultdict(list)

    # look for neighbors for each atom in the structure
    for i, atom in enumerate(structure.atoms):
        atom.neighbors = []

        # center on the atom so that its voronoi cell is fully described
        new_struct.recenter(atom, middle=True)
        tess = Voronoi(new_struct.cartesian_coords)
        for j, r in enumerate(tess.ridge_points):
            if not i in r: # only ridges involving the specified atom matter
                continue
            inds = tess.ridge_vertices[j]
            verts = tess.vertices[inds]

            # check that the area of the facet is large enough
            if _get_facet_area(verts) < tol:
                continue

            # Get the indices of all points which this atom shares a ridge with
            ind = [k for k in tess.ridge_points[j] if k != i ][0]
            # map the atom index back into the original cell. 
            atom.neighbors.append(atom)
        nns[atom] = atom.neighbors
    return nns
