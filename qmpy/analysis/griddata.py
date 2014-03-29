# qmpy/analysis/griddata

import numpy as np
import numpy.linalg as la
import qmpy.utils as utils
import itertools

class GridData():
    """
    Container for 3d data, e.g. charge density or electron localization
    function.

    """
    def __init__(self, data, lattice=None):
        """
        Arguments:
            data: M x N x O sequence of data.
            mesh: 
            spacing: 
        """
        self.data = np.array(data)
        self.grads = np.gradient(data)
        self.mesh = np.array(self.data.shape)
        self.spacing = 1./self.mesh
        if lattice is None:
            lattice = np.eye(3)
        self.lattice = lattice
        self.inv = la.inv(lattice)

    def ind_to_cart(self, ind):
        """
        Converts an [i,j,k] index to [X,Y,Z] cartesian coordinate.
        """
        return np.dot(self.spacing*ind, self.lattice)

    def ind_to_coord(self, ind):
        """
        Converts an [i,j,k] index to [x,y,z] frational coordinate.
        """
        return utils.wrap(self.spacing*ind)

    def cart_to_coord(self, cart):
        return utils.wrap(np.dot(self.inv.T, cart))

    def interpolate(self, point, cart=False):
        """
        Calculates the value at `point` using trilinear interpolation.

        Arguments:
            point: point to evaluate the value at.

        Keyword Arguments:
            cart: If True, the point is taken as a cartesian coordinate. If
            not, it is assumed to be in fractional coordinates. default=False. 
        """
        if cart:
            point = self.cart_to_coord(point)
        point = utils.wrap(point)

        x0,y0,z0 = ( int(np.floor(point[0]*self.mesh[0])),
            int(np.floor(point[1]*self.mesh[1])),
            int(np.floor(point[2]*self.mesh[2])) )
        x,y,z = ( (point[0]*self.mesh[0]) % 1,
                  (point[1]*self.mesh[1]) % 1,
                  (point[2]*self.mesh[2]) % 1)
        x1,y1,z1 = ( (x0+1) % self.mesh[0], 
                     (y0+1) % self.mesh[1], 
                     (z0+1) % self.mesh[2] )
        interp_val = ( self.data[x0,y0,z0]*(1-x)*(1-y)*(1-z) +
                       self.data[x1,y0,z0]*x*(1-y)*(1-z) +
                       self.data[x0,y1,z0]*(1-x)*y*(1-z) +
                       self.data[x0,y0,z1]*(1-x)*(1-y)*z +
                       self.data[x1,y1,z0]*x*y*(1-z) +
                       self.data[x1,y0,z1]*x*(1-y)*z +
                       self.data[x0,y1,z1]*(1-x)*y*z +
                       self.data[x1,y1,z1]*x*y*z )
        return interp_val

    def local_min(self, index):
        """
        Starting from `index` find the local value minimum.

        Returns:
            index: shape (3,) index of local minimum.
            value: Value of grid at the local minimum.

        """
        ## TODO: support inputs of 'coord' or 'cart'

        neighbors = list(itertools.permutations([-1,0,1], r=3))
        neighbors = [ np.array(index) + n for n in neighbors ]
        neighbors = [ n % self.mesh for n in neighbors ]
        values = [ self.data[tuple(n)] for n in neighbors ]
        print values

        lowest = np.argsort(values)[0]
        print lowest
        if values[lowest] < self.data[tuple(index)]:
            return self.local_min(neighbors[lowest])
        return index, self.data[tuple(index)]
    
    def find_min_coord(self, N=1):
        """
        Find the `N` lowest valued indices.
        """
        coords = []
        coord_vector = self.data.flatten()
        sorted_inds = list(coord_vector.argsort())
        count = 0
        while N > 0:
            min_ind = unravel_index(sorted_inds[count], self.mesh)
            count += 1
            if ( self.local_min(min_ind) and
                    self.data[min_ind[0],min_ind[1],min_ind[2]] > 0) :
                coords.append(np.array(min_ind)*self.spacing)
                N-=1
        return coords

    def path(self, origin, end):
        """
        Gets a 1D array of values for a line connecting `origin` and `end`.
        """
        path_dens = []
        origin = np.array([ float(i) for i in origin ])
        end = np.array([ float(i) for i in end ])
        result = []
        for i in np.mgrid[0:1:50j]:
            point = (1-i)*origin + i*end
            result.append((i,self.interpolate(point)))
        return result

    def slice(self, point, orientation):
        """
        Return a 2D array of values for a slice through the GridData passing
        through `point` with normal vector `orientation`.
        """
        res = int(max(self.mesh)/3.0)
        orientation = [ float(x) for x in orientation ]
        point = [ float(x) for x in point ]
        slice_vals = np.zeros((res,res))
        slice_coords = np.zeros((res,res))
        a,b,c = orientation
        x0,y0,z0 = point
        if c != 0:
            for i in range(res):
                for j in range(res):
                    x=float(i)/float(res)
                    y=float(j)/float(res)
                    slice_coords[i,j] = (-(a*(x-x0)+b*(y-y0))/c+z0)%1
                    slice_vals[i,j] = self.interpolate(
                            np.array([x,y,slice_coords[i,j]]))
        elif b != 0:
            for i in range(res):
                for k in range(res):
                    x=float(i)/float(res)
                    z=float(k)/float(res)
                    slice_coords[i,k] = (-(a*(x-x0)+c*(z-z0))/b+y0)%1
                    slice_vals[i,k] = self.interpolate(
                            np.array([x,slice_coords[i,k],z]))
        elif a != 0:
            for j in range(res):
                for k in range(res):
                    y=float(j)/float(res)
                    z=float(k)/float(res)
                    slice_coords[j,k] = (-(b*(y-y0)+c*(z-z0))/a+x0)%1
                    slice_vals[j,k] = self.interpolate(
                            np.array([slice_coords[j,k],y,z]))
        return slice_vals,slice_coords
