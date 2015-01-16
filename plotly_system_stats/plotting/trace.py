import datetime

import plotly.graph_objs as pl_graph_objs

from plotly_system_stats.plotting.plot_config import plot_config
from plotly_system_stats.plotting.stream import Stream


class Trace(object):
    def __init__(self, **kwargs):
        self.plot = kwargs.get('plot')
        self.metric = kwargs.get('metric')
        stream_id = self.get_conf('stream_id')
        if stream_id is None:
            self.stream = Stream(trace=self)
            self.stream_id = self.stream.stream_id
            self.set_conf('stream_id', self.stream_id)
        else:
            self.stream_id = stream_id
            self.stream = Stream(stream_id=stream_id, trace=self)
        self.pl_trace = pl_graph_objs.Scatter(x=[], y=[], name=self.id, 
                                              stream={'token':self.stream_id})
    @property
    def id(self):
        return self.metric.name
    def get_conf(self, key, default=None):
        d = self.plot.get_conf('traces', {}).get(self.id)
        if d is None:
            return default
        return d.get(key, default)
    def set_conf(self, key, item):
        traces = self.plot.get_conf('traces')
        if traces is None:
            traces = {}
            self.plot.set_conf('traces', traces)
        d = traces.get(self.id)
        if d is None:
            d = {}
            traces[self.id] = d
        d[key] = item
        plot_config.write_all()
    def update_value(self, **kwargs):
        now = kwargs.get('now')
        value = kwargs.get('value')
        if False:# now is None:
            dt = datetime.datetime.now()
        else:
            dt = datetime.datetime.fromtimestamp(now)
        self.stream.write({'x':dt, 'y':value})

class SubplotTrace(Trace):
    def __init__(self, **kwargs):
        super(SubplotTrace, self).__init__(**kwargs)
        for key, val in self.axis_indecies.iteritems():
            val = '%s%s' % (key, val)
            self.pl_trace['%saxis' % (key)] = val
    @property
    def axis_indecies(self):
        return self.plot.axis_indecies
    
