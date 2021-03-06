import time
import platform
from collections import OrderedDict

from plotly_system_stats.config import config
from plotly_system_stats.stat_collection.collection.collector import Collector
from plotly_system_stats.stat_collection.sources import SOURCE_CLASSES
from plotly_system_stats.plotting.figure import Figure

class Main(object):
    def __init__(self, **kwargs):
        self.running = False
        self.sources = OrderedDict()
        self.collector = Collector()
        self.collector.value_change_callbacks.bind(self.on_source_value_change)
        for source_conf in config.get('sources', []):
            self.add_source(**source_conf)
        if not len(self.sources):
            for cls in SOURCE_CLASSES.itervalues():
                if not hasattr(cls, 'build_defaults'):
                    continue
                for source_conf in cls.build_defaults():
                    self.add_source(**source_conf)
            self.update_conf()
        self.figures = {}
        for key, conf_data in config.get('plotly', {}).get('figures', {}).iteritems():
            fkwargs = conf_data.copy()
            fkwargs.update(dict(main=self, id=key))
            figure = Figure(**fkwargs)
            self.figures[figure.id] = figure
        if not len(self.figures):
            fig_id = '_'.join([platform.node(), 'system_stats'])
            figure = Figure(main=self, sources=self.sources.values(), id=fig_id)
            self.figures[figure.id] = figure
        #self.figure = Figure(main=self, sources=self.sources.values())
    def add_source(self, **kwargs):
        cls = kwargs.get('cls')
        if cls is None:
            cls_name = kwargs.get('cls_name')
            cls = SOURCE_CLASSES.get(cls_name)
        obj = cls(**kwargs)
        self.sources[obj.name] = obj
        self.collector.add_source(obj)
        return obj
    def update_conf(self):
        sources = []
        for source in self.sources.itervalues():
            sources.append(source.get_conf_data())
        config.set('sources', sources)
    def on_source_value_change(self, **kwargs):
        pass
    def mainloop(self):
        self.start()
        try:
            while self.running:
                time.sleep(1.)
        except KeyboardInterrupt:
            self.stop()
    def start(self):
        self.running = True
        self.collector.start()
    def stop(self):
        self.collector.stop()
        self.running = False
        
