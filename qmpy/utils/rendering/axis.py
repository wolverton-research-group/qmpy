import logging

from renderable import *
import qmpy

logger = logging.getLogger(__name__)

class Axis(object):
    def __init__(self, name, label='', units='', 
                       template='{label} [{units}]', 
                       **kwargs):
        self.name = name
        self.label = label
        self.units = units
        self.template = template
        self.min = None
        self.max = None
        self.options = kwargs

    @property
    def axis_label(self):
        if self.units:
            return self.template.format(label=self.label, units=self.units)
        else:
            return self.label

    def apply_to_matplotlib(self, **kwargs):
        axes = kwargs.get('axes', plt.gca())
        if self.name == 'x':
            ax = axes.xaxis
        elif self.name == 'y':
            ax = axes.yaxis
        elif self.name == 'z':
            ax = axes.zaxis

        lim = list(getattr(plt, self.name+'lim')())
        if not self.min is None:
            lim[0] = self.min
        if not self.max is None: 
            lim[1] = self.max
        getattr(plt, self.name+'lim')(lim)
        getattr(plt, self.name+'label')(self.axis_label)
        return plt.gca()

    def update_flot_settings(self, renderer):
        renderer.options[self.name+'axis'].update(self.options)
        if not self.max is None:
            renderer.options[self.name+'axis']['max'] = self.max
        if not self.min is None:
            renderer.options[self.name+'axis']['min'] = self.min
        if self.label:
            renderer.options[self.name+'axis']['axisLabel'] = self.axis_label
