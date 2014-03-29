import sys
import logging
import json

from renderable import *
import qmpy
import point
import line
import text
import axis

logger = logging.getLogger(__name__)

class Renderer(object):
    def __init__(self, format='matplotlib', 
            lines=[], points=[], point_collections=[], text=[],
            **kwargs):
        self.format = format
        self.lines = list(lines)
        self.points = list(points)
        self.point_collections = list(point_collections )
        self.text = list(text)
        self.xaxis = axis.Axis('x')
        self.yaxis = axis.Axis('y')
        self.zaxis = axis.Axis('z')
        self.options = {'legend':{},
                        'xaxis':{},
                        'yaxis':{},
                        'zaxis':{},
                        'series':{},
                        'grid':{},
                        'interaction':{}}
        self.options.update(kwargs)

    def clear(self):
        self.lines = []
        self.points = []
        self.point_collections = []
        self.text = []
        self.xaxis = axis.Axis()
        self.yaxis = axis.Axis()
        self.zaxis = axis.Axis()
        self.options = {'legend':{},
                        'xaxis':{},
                        'yaxis':{},
                        'series':{},
                        'grid':{},
                        'interaction':{}}

    @property
    def dim(self):
        if self.points:
            return self.points[0].dim
        elif self.lines:
            return self.lines[0].dim
        elif self.point_collections:
            return self.point_collections[0].dim
        elif self.text:
            return self.text[0].dim
        else:
            return None

    def get_flot_script(self, div="placeholder", **kwargs):
        data = []
        for line in self.lines:
            data.append(line.get_flot_series())
        for pt in self.points:
            data.append(pt.get_flot_series())
        for pc in self.point_collections:
            data.append(pc.get_flot_series())

        self.xaxis.update_flot_settings(self)
        self.yaxis.update_flot_settings(self)

        cmd = 'var placeholder = $("#{div}");'.format(div=div)
        cmd += '\nvar data = %s;' % json.dumps([ d for d in data if d ])

        cmd += '\nvar plot = $.plot(placeholder, data, {options});'.format(
                options=json.dumps(self.options))

        if self.text:
            cmd += '\n var o = plot.pointOffset({ x: 0, y: 0 });'
        for text in self.text:
            cmd += '\n' + text.get_flot_series()
        return cmd

    def plot_in_matplotlib(self, **kwargs):
        if 'axes' in kwargs:
            axes = kwargs['axes']
        elif self.dim == 2:
            fig = plt.figure()
            axes = fig.add_subplot(111)
        elif self.dim == 3:
            fig = plt.figure()
            axes = fig.gca(projection='3d')
        else:
            print "I don't know how to display a {d}-D image".format(d=self.dim)
            raise RenderingError
                    
        for line in self.lines:
            line.draw_in_matplotlib(axes=axes)
        for point in self.points:
            point.draw_in_matplotlib(axes=axes)
        for pc in self.point_collections:
            pc.draw_in_matplotlib(axes=axes)
        for text in self.text:
            text.draw_in_matplotlib(axes=axes)

        self.xaxis.apply_to_matplotlib(axes=axes)
        self.yaxis.apply_to_matplotlib(axes=axes)
        return axes

    def add(self, *objects):
        for obj in objects:
            if isinstance(obj, point.Point):
                self.points.append(obj)
            elif isinstance(obj, line.Line):
                self.lines.append(obj)
            elif isinstance(obj, text.Text):
                self.text.append(obj)
            elif isinstance(obj, point.PointCollection):
                self.point_collections.append(obj)
            else:
                raise TypeError(obj, 'must be a renderable object')

    def __call__(self, format=None, **kwargs):
        if format is None:
            return self.__call__(self.format, **kwargs)
        if format == 'matplotlib':
            return self.plot_in_matplotlib(**kwargs)
        elif format == 'flot':
            return self.get_flot_script(**kwargs)
