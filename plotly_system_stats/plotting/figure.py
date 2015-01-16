from collections import OrderedDict

import plotly.plotly as pl
import plotly.graph_objs as pl_graph_objs

from plotly_system_stats.plotting.plot_config import plot_config
from plotly_system_stats.plotting.plot import SubPlot

class Figure(object):
    def __init__(self, **kwargs):
        self.main = kwargs.get('main')
        self.id = kwargs.get('id')
        if self.id is None:
            self.get_unique_id()
        self.filename = self.get_conf('filename')
        if self.filename is None:
            self.filename = self.id
            self.set_conf('filename', self.filename)
        self.plots = OrderedDict()
        for plot_id in self.get_conf('plot_ids', []):
            self.add_subplot(source_id=plot_id)
        if not len(self.plots):
            for source in kwargs.get('sources', []):
                self.add_subplot(source=source)
        self.set_conf('plot_ids', [plot.id for plot in self.plots.values()])
        self.pl_data = pl_graph_objs.Data([t.pl_trace for t in self.iter_traces()])
        
        self.build_layout()
        self.pl_figure = pl_graph_objs.Figure(data=self.pl_data, layout=self.pl_layout)
        self.url = pl.plot(self.pl_figure, filename=self.filename, auto_open=False)
    def get_unique_id(self):
        d = plot_config.get('figures')
        if not len(d.keys()):
            key = '0'
        else:
            key = str(max([int(k) for k in d.keys() if k.isdigit()]))
        self.id = key
        d[key] = {}
        plot_config.write_all()
    def build_layout(self):
        kwargs = {}
        sizes = self.calc_plot_sizes()
        last_anchor = None
        for size, plot in zip(sizes, self.plots.values()):
            akwargs = {'x':{}, 'y':{}}
            akwargs['y']['domain'] = size
            if last_anchor is not None:
                akwargs['x']['anchor'] = last_anchor
            for trace in plot.traces.itervalues():
                tr_keys = trace.axis_pl_keys
                tr_vals = trace.axis_pl_vals
                yaxis = pl_graph_objs.YAxis(**akwargs['y'])
                kwargs[tr_keys['y']] = yaxis
                if len(akwargs['x']):
                    xaxis = pl_graph_objs.XAxis(**akwargs['x'])
                    kwargs[tr_keys['x']] = xaxis
                last_anchor = tr_vals['y']
        self.pl_layout = pl_graph_objs.Layout(**kwargs)
    def calc_plot_sizes(self):
        count = len(self.plots)
        spacing = .3 / count
        height = (1 - spacing * (count - 1)) / count
        l = []
        for i in range(count):
            start = (height + spacing) * i
            end = start + height
            l.append([start, end])
        return l
    def get_next_axis_indecies(self):
        d = {'x':1, 'y':1}
        for plot in self.plots.itervalues():
            for key, val in plot.axis_indecies.iteritems():
                if val >= d[key]:
                    d[key] = val + 1
        d['x'] = 1
        return d
    def get_conf(self, key, default=None):
        return plot_config.get('figures').get(self.id, {}).get(key, default)
    def set_conf(self, key, item):
        d = plot_config.get('figures').get(self.id)
        if d is None:
            d = {}
            plot_config.get('figures')[self.id] = d
        d[key] = item
        plot_config.write_all()
    def add_subplot(self, **kwargs):
        kwargs.setdefault('figure', self)
        kwargs.setdefault('main', self.main)
        obj = SubPlot(**kwargs)
        self.plots[obj.id] = obj
        plot_ids = self.get_conf('plot_ids', [])
        if obj.id not in plot_ids:
            plot_ids.append(obj.id)
            self.set_conf('plot_ids', plot_ids)
        return obj
    def iter_traces(self):
        for plot in self.plots.itervalues():
            for trace in plot.traces.itervalues():
                yield trace
    
