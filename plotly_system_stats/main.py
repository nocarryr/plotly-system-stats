from collections import OrderedDict
from plotly_system_stats.config import Config
from plotly_system_stats.stat_collection.collection.collector import Collector
from plotly_system_stats.stat_collection.sources import SOURCE_CLASSES

class Main(object):
    def __init__(self, **kwargs):
        self.config = Config()
        self.sources = OrderedDict()
        self.collector = Collector(value_change_callback=self.on_source_value_change)
        for source_conf in self.config.get('sources', []):
            self.add_source(**source_conf)
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
        self.config.set('sources', sources)
    def on_source_value_change(self, **kwargs):
        pass
