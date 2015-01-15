from collections import OrderedDict

import plotly.plotly as pl
import plotly.graph_objs as pl_graph_objs
import plotly.tools as pl_tools

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
        ## TODO: this doesn't get loaded correctly
        #for plot_id in self.get_conf('plot_ids', []):
        #    self.add_subplot(source_id=plot_id)
        if not len(self.plots):
            for source in kwargs.get('sources', []):
                self.add_subplot(source=source)
        self.set_conf('plot_ids', [plot.id for plot in self.plots.values()])
        self.pl_data = pl_graph_objs.Data([t.pl_trace for t in self.iter_traces()])
        cols = 2
        rows = 1
        if len(self.plots) > cols:
            rows = len(self.plots) / 2
            if len(self.plots) < cols * rows:
                rows += 1
        self.pl_figure = pl_tools.get_subplots(rows=rows, columns=cols)
        self.pl_figure['data'] += self.pl_data
        self.url = pl.plot(self.pl_figure, filename=self.filename, 
                           fileopt='extend', auto_open=False)
    def get_unique_id(self):
        d = plot_config.get('figures')
        if not len(d.keys()):
            key = '0'
        else:
            key = str(max([int(k) for k in d.keys() if k.isdigit()]))
        self.id = key
        d[key] = {}
        plot_config.write_all()
    def get_conf(self, key, default=None):
        return plot_config.get('figures').get(self.id, {}).get(key, default)
    def set_conf(self, key, item):
        d = plot_config.get('figures').get(self.id)
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
