from collections import OrderedDict

from plotly_system_stats.plotting.plot_config import plot_config
from plotly_system_stats.plotting.trace import Trace, SubplotTrace

class BasePlot(object):
    trace_cls = Trace
    def __init__(self, **kwargs):
        self.main = kwargs.get('main')
        self.source = kwargs.get('source')
        self.source_id = kwargs.get('source_id')
        if self.source is None:
            self.source = self.main.sources[self.source_id]
        else:
            self.source_id = self.source.name
            self.set_conf('source_id', self.source_id)
        self.traces = OrderedDict()
        for metric in self.source.metrics.itervalues():
            self.add_trace(metric=metric)
        self.source.value_change_callbacks.bind(self.on_source_value_change)
    @property
    def id(self):
        return self.source.name
    def get_conf(self, key, default=None):
        d = plot_config.get('plots').get(self.id)
        if d is None:
            return default
        return d.get(key, default)
    def set_conf(self, key, item):
        d = plot_config.get('plots').get(self.id)
        if d is None:
            d = {}
            plot_config.get('plots')[self.id] = d
        d[key] = item
        plot_config.write_all()
    def add_trace(self, **kwargs):
        kwargs.setdefault('plot', self)
        trace = self.trace_cls(**kwargs)
        self.traces[trace.id] = trace
        return trace
    def on_source_value_change(self, **kwargs):
        metric = kwargs.get('metric')
        trace = self.traces.get(metric.name)
        if trace:
            trace.update_value(**kwargs)
    
class Plot(BasePlot):
    def __init__(self, **kwargs):
        super(Plot, self).__init__(**kwargs)
        self.filename = self.get_conf('filename')
        if self.filename is None:
            self.filename = self.source.name
            self.set_conf('filename', self.filename)
        
        self.url = self.get_conf('url')
        
    
class SubPlot(BasePlot):
    trace_cls = SubplotTrace
    def __init__(self, **kwargs):
        self.figure = kwargs.get('figure')
        self.index = kwargs.get('index')
        super(SubPlot, self).__init__(**kwargs)
    def get_next_index(self):
        self.index = self.get_conf('index')
        if self.index is None:
            self.index = len(self.figure.plots)
            self.set_conf('index', self.index)
    def add_trace(self, **kwargs):
        if self.index is None:
            self.get_next_index()
        self.axis_indecies = self.get_conf('axis_indecies')
        if self.axis_indecies is None:
            self.axis_indecies = self.figure.get_next_axis_indecies()
            self.set_conf('axis_indecies', self.axis_indecies)
        return super(SubPlot, self).add_trace(**kwargs)
