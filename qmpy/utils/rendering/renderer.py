import sys
import logging
import json

from renderable import *
import qmpy
import point
import line
import text
import axis
from qmpy.utils import *

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


    def _write_matplotlib_text(self, px, py, p, **kwargs):
        stable = kwargs['stable']
        if not stable:
            fs = 20 
        else:
            fs = 32
    
        if abs(px-0.5) < 0.005 and abs(py-0.866) < 0.005:
            px -= 0.055; 
            return 'ax.text(%s, %s, r"%s", fontsize=%s)\n' %(px, py, p, fs)
        if abs(px-0.0) < 0.005 and abs(py-0.0) < 0.005:
            px -= 0.055; py -= 0.025 
            return 'ax.text(%s, %s, r"%s", fontsize=%s)\n' %(px, py, p, fs)
        if abs(px-1.0) < 0.005 and abs(py-0.0) < 0.005:
            px += 0.025; py -= 0.025
            return 'ax.text(%s, %s, r"%s", fontsize=%s)\n' %(px, py, p, fs)
    
        if py < 0.005:
            py -= 0.070 if stable else 0.045
            px -= 0.055 if stable else 0.025
        else:
            py -= 0.005
            px += 0.020 if stable else 0.010
         
        return 'ax.text(%s, %s, r"%s", fontsize=%s)\n' %(px, py, p, fs)

    def write_matplotlib_script_bk(self, **kwargs):
        prefixes = {0:'unary', 1:'binary', 2:'ternary', 3:'quaternary',
                4:'graph'}
        prefix = kwargs['prefix'] if 'prefix' in kwargs else prefixes[self.dim]
        hd = kwargs['hull_distance'] if 'hull_distance' in kwargs else False
        fo = open(prefix+'_hull_mpl.py', 'w')
        
        fo.write('# import statements go here\n')
        fo.write('import matplotlib as mpl\n')
        fo.write('import matplotlib.pyplot as plt\n')
        fo.write('from matplotlib import rc\n')
        fonts = ["New Century Schoolbook", "Times", "Palatino", "serif"]
        fo.write('rc("font",**{"family":"serif","serif":%s})\n' %(fonts))
        fo.write('rc("font",**{"weight":"bold"})\n')
        fo.write('rc("text", usetex=True)\n')
        fo.write('\n')

        fo.write('# initialize the mpl figure, and add a big subplot\n')
        fo.write('fig = plt.figure(figsize=(10,8.7))\n')
        fo.write('ax = fig.add_subplot(111)\n')
        fo.write('\n')
        
        fo.write('# plot all the tie lines in the hull\n')
        for line in self.lines:
            px = [ p.coord[0] for p in line.points ]
            py = [ p.coord[1] for p in line.points ]
            fo.write('ax.plot(%s, %s, c="#AAAAAA", lw=3.0)\n' %(px, py))
        fo.write('\n')
        
        unstable = self.point_collections[0].points
        fo.write('# plot all the unstable phases (red)\n')
        phases = set()
        for p in unstable: 
            px = p.coord[0]; py = p.coord[1]
            pname = p.label.split(':')[0]
            if pname in phases:
                continue
            phases.add(pname)
            pname = r'%s' %(format_bold_latex(parse_comp(pname)))
            if hd:
                pstab = p.options['hull_distance']
                pname = '%s (%0.3f)' %(pname, pstab)
            penergy = float(p.label.split(':')[1].split()[0])
            fo.write('ax.plot(%s, %s, c="crimson", marker="o", ms=10.0, mew=0.0)\n' %(px, py))
            fo.write(self._write_matplotlib_text(px, py, pname, stable=False))
        fo.write('\n')
        
        stable = self.point_collections[1].points
        fo.write('# plot all the stable phases (forestgreen)\n')
        for p in stable:
            px = p.coord[0]; py = p.coord[1]
            pname = p.label.split(':')[0]
            pname = r'%s' %(format_bold_latex(parse_comp(pname)))
            penergy = float(p.label.split(':')[1].split()[0])
            fo.write('ax.plot(%s, %s, c="forestgreen", marker="o", ms=18.0, mew=0.0)\n' %(px, py))
            fo.write(self._write_matplotlib_text(px, py, pname, stable=True))
        fo.write('\n')
        
        fo.write('# change axis limits and make axes invisible\n')
        fo.write('ax.set_xlim(-0.05, 1.05)\n')
        fo.write('ax.set_ylim(-0.05, 0.90)\n')
        fo.write('ax.set_axis_off()\n')
        fo.write('\n')
        
        fo.write('# save the plot in a PDF\n')
        fo.write('plt.savefig("%s_hull.pdf", bbox_inches="tight", dpi=300)\n' %(prefix))

    ### Mohan
    def write_matplotlib_script(self, **kwargs):
        prefixes = {0:'unary', 1:'binary', 2:'ternary', 3:'quaternary',
                4:'graph'}
        prefix = kwargs['prefix'] if 'prefix' in kwargs else prefixes[self.dim]
        hd = kwargs['hull_distance'] if 'hull_distance' in kwargs else False
        fo = open(prefix+'_hull_mpl.py', 'w')
        
        fo.write('# import statements go here\n')
        fo.write('import matplotlib as mpl\n')
        fo.write('import matplotlib.pyplot as plt\n')
        fo.write('from matplotlib import rc\n')
        fonts = ["New Century Schoolbook", "Times", "Palatino", "serif"]
        fo.write('rc("font",**{"family":"serif","serif":%s})\n' %(fonts))
        fo.write('rc("font",**{"weight":"bold"})\n')
        fo.write('rc("text", usetex=True)\n')
        fo.write('\n')

        fo.write('# initialize the mpl figure, and add a big subplot\n')
        fo.write('fig = plt.figure(figsize=(10,8.7))\n')
        fo.write('ax = fig.add_subplot(111)\n')
        fo.write('\n')

        fo.write('''
# Function to get the shift of each label
def _shift(p,stable=True):
    px, py = p
    if abs(px-0.5) < 0.005 and abs(py-0.866) < 0.005:
        sx = -0.055; sy = 0;
    if abs(px-0.0) < 0.005 and abs(py-0.0) < 0.005:
        sx = -0.055; sy = -0.025 
    if abs(px-1.0) < 0.005 and abs(py-0.0) < 0.005:
        sx =  0.025;  sy = -0.025

    if py < 0.005:
        sy = -0.070 if stable else -0.045
        sx = -0.055 if stable else -0.025
    else:
        sy = -0.005
        sx =  0.020 if stable else 0.010

    return [sx,sy]

# Function to plot tie lines
def plot_tielines(px,py,**kwargs):
    lw = kwargs.get('lw',3.0)
    lc = kwargs.get('lc','#AAAAAA')
    ls = kwargs.get('ls','-')
    ax.plot(px,py,c=lc,lw=lw,ls=ls)

# Function to plot stable phases
def stable(p,name=None,**kwargs):
    marker   = kwargs.get('marker','o')
    ms       = kwargs.get('ms','18')
    mfc      = kwargs.get('mfc','forestgreen')
    mec      = kwargs.get('mec','none')
    mew      = kwargs.get('mew','0.0')
    fontsize = kwargs.get('fontsize',32)
    label    = kwargs.get('label',True)
    xshift   = kwargs.get('xshift',_shift(p,stable=True)[0])
    yshift   = kwargs.get('yshift',_shift(p,stable=True)[1])
    ax.plot(p[0],p[1],marker=marker,ms=ms,mfc=mfc,mec=mec,mew=mew)
    if label and name:
        ax.text(p[0]+xshift,p[1]+yshift,name,fontsize=fontsize)

# Function to plot unstable phases
def unstable(p,name=None,**kwargs):
    marker   = kwargs.get('marker','o')
    ms       = kwargs.get('ms','10')
    mfc      = kwargs.get('mfc','crimson')
    mec      = kwargs.get('mec','none')
    mew      = kwargs.get('mew','0.0')
    fontsize = kwargs.get('fontsize',20)
    label    = kwargs.get('label',True)
    xshift   = kwargs.get('xshift',_shift(p,stable=False)[0])
    yshift   = kwargs.get('yshift',_shift(p,stable=False)[1])
    ax.plot(p[0],p[1],marker=marker,ms=ms,mfc=mfc,mec=mec,mew=mew)
    if label and name:
        ax.text(p[0]+xshift,p[1]+yshift,name,fontsize=fontsize)
        ''')
        
        fo.write('\n')

        fo.write('# plot all the tie lines in the hull\n')
        for line in self.lines:
            px = [ p.coord[0] for p in line.points ]
            py = [ p.coord[1] for p in line.points ]
            fo.write('plot_tielines(%s, %s)\n' %(px, py))
        fo.write('\n')
        
        unstable = self.point_collections[0].points
        fo.write('# plot all the unstable phases \n')
        phases = set()
        for p in unstable: 
            px = p.coord[0]; py = p.coord[1]
            pname = p.label.split(':')[0]
            if pname in phases:
                continue
            phases.add(pname)
            pname = r'%s' %(format_bold_latex(parse_comp(pname)))
            if hd:
                pstab = p.options['hull_distance']
                pname = '%s (%0.3f)' %(pname, pstab)
            penergy = float(p.label.split(':')[1].split()[0])
            fo.write('unstable([%s,%s],r"%s")\n' %(px, py, pname))
        fo.write('\n')
        
        stable = self.point_collections[1].points
        fo.write('# plot all the stable phases \n')
        for p in stable:
            px = p.coord[0]; py = p.coord[1]
            pname = p.label.split(':')[0]
            pname = r'%s' %(format_bold_latex(parse_comp(pname)))
            penergy = float(p.label.split(':')[1].split()[0])
            fo.write('stable([%s,%s],r"%s")\n' %(px, py, pname))
        fo.write('\n')
        
        fo.write('# change axis limits and make axes invisible\n')
        fo.write('ax.set_xlim(-0.05, 1.05)\n')
        fo.write('ax.set_ylim(-0.05, 0.90)\n')
        fo.write('ax.set_axis_off()\n')
        fo.write('\n')
        
        fo.write('# save the plot in a PDF\n')
        fo.write('plt.savefig("%s_hull.pdf", bbox_inches="tight", dpi=300)\n' %(prefix))


    def write_phase_coordinates(self, **kwargs):
        prefixes = {0:'unary', 1:'binary', 2:'ternary', 3:'quaternary',
                4:'graph'}
        prefix = kwargs['prefix'] if 'prefix' in kwargs else prefixes[self.dim]
        fo = open(prefix+'_coordinates.csv', 'w')
        
        ##for line in self.lines:
        ##    px = [ p.coord[0] for p in line.points ]
        ##    py = [ p.coord[1] for p in line.points ]
        ##    fo.write('ax.plot(%s, %s, c="#AAAAAA", lw=3.0)\n' %(px, py))
        ##fo.write('\n')
        
        unstable = self.point_collections[0].points
        phases = set()
        for p in unstable: 
            px = p.coord[0]; py = p.coord[1]
            pname = p.label.split(':')[0]
            if pname in phases:
                continue
            phases.add(pname)
            penergy = float(p.label.split(':')[1].split()[0])
            fo.write("%s,%s,%s,%s\n" %(pname, px, py, penergy))
        
        stable = self.point_collections[1].points
        for p in stable:
            px = p.coord[0]; py = p.coord[1]
            pname = p.label.split(':')[0]
            penergy = float(p.label.split(':')[1].split()[0])
            fo.write("%s,%s,%s,%s\n" %(pname, px, py, penergy))
        

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
    
