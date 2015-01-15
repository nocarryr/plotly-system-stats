from plotly_system_stats.utils import WeakCallbacks
from plotly_system_stats.stat_collection.collection.scheduler import Scheduler

class Collector(object):
    def __init__(self, **kwargs):
        self.sources = {}
        self.value_change_callbacks = WeakCallbacks()
        self.scheduler = kwargs.get('scheduler')
        if self.scheduler is None:
            self.scheduler = Scheduler()
        self.scheduler.callback = self.on_scheduler_interval
        for source in kwargs.get('sources', []):
            self.add_source(source)
    @property
    def running(self):
        return self.scheduler.running.is_set()
    def start(self):
        self.scheduler.start()
    def stop(self):
        self.scheduler.stop()
    def add_source(self, source):
        self.sources[source.name] = source
        source.value_change_callbacks.bind(self.on_source_value_change)
        if source.update_interval < self.scheduler.interval:
            self.scheduler.interval = source.update_interval
    def on_scheduler_interval(self):
        for source in self.sources.itervalues():
            source.update_metrics()
    def on_source_value_change(self, **kwargs):
        self.value_change_callbacks(**kwargs)
