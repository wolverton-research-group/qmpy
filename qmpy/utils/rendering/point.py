import numpy as np
import logging

import qmpy
from renderable import *

logger = logging.getLogger(__name__)

class Point(Renderable):
    def __init__(self, coord, label=None, **kwargs):
        if isinstance(coord, Point):
            self.coord = list(coord.coord)
            self.label = coord.label
            self.options = coord.options
            self.options.update(kwargs)
        else:
            self.coord = list(coord)
            self.label = label
            self.options = kwargs

    def __eq__(self, other):
        if not np.allclose(self.coord, other.coord):
            return False
        if not self.label == other.label:
            return False
        return True

    @property
    def dim(self):
        return len(self.coord)

    def draw_in_matplotlib(self, **kwargs):
        if not kwargs.get('axes'):
            axes = plt.gca()
        else:
            axes = kwargs['axes']
        options = dict(self.options)
        options.update(kwargs)
        axes.scatter(*self.coord, **options)
        #if self.label:
        #    plt.text(x, y, self.label)

    def get_flot_series(self, **kwargs):
        pc = PointCollection([self], **self.options)
        return pc.get_flot_series()

class PointCollection(Renderable):
    def __init__(self, points, label=None, fill=False, **kwargs):
        self.points = [ Point(pt) for pt in points ]
        self.label = label
        self.fill = fill
        self.options = kwargs

    @property
    def as_pairs(self):
        return [ pt.coord for pt in self.points ]

    @property
    def as_axes(self):
        return [ [ pt.coord[i] for pt in self.points ]
                   for i in range(self.dim) ]

    def draw_in_matplotlib(self, **kwargs):
        options = dict(self.options)
        options.update(kwargs)
        for point in self.points:
            point.draw_in_matplotlib(**options)

    def get_flot_series(self, **kwargs):
        series = {'data': self.as_pairs, 'points':{'show':True,
            'fill':self.fill}} 
        if self.label:
            series['label'] = self.label
        series.update(self.options)
        series['labels'] = [ pt.label for pt in self.points ]
        series.update(kwargs)
        return series

    @property
    def dim(self):
        return min([p.dim for p in self.points ])
