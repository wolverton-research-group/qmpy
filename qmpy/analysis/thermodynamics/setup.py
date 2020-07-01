from distutils.core import setup
from Cython.Build import cythonize

setup(
        name = 'ConvexHull',
        ext_modules = cythonize("convex_hull.pyx"),
        )
