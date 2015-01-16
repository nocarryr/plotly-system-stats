import time
from collections import OrderedDict

from plotly_system_stats.utils import WeakCallbacks

class BaseSource(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        if not hasattr(self, 'update_interval'):
            self.update_interval = kwargs.get('update_interval', 4.)
        self.value_change_callbacks = WeakCallbacks()
        self.metrics = OrderedDict()
    def add_metric(self, cls, **kwargs):
        kwargs.setdefault('source', self)
        obj = cls(**kwargs)
        self.metrics[obj.name] = obj
        return obj
    def update_metrics(self, *args, **kwargs):
        now = kwargs.get('now')
        if now is None:
            now = time.time()
            kwargs.setdefault('now', now)
        for obj in self.metrics.itervalues():
            if not obj.update_needed(*args, **kwargs):
                continue
            obj.update(*args, **kwargs)
    def on_metric_value_changed(self, **kwargs):
        kwargs.setdefault('source', self)
        self.value_change_callbacks(**kwargs)
    def get_conf_data(self):
        d = dict(cls_name=self.__class__.__name__, name=self.name, metrics=[])
        for obj in self.metrics.itervalues():
            d['metrics'].append(obj.get_conf_data())
        return d
        
        
class BaseMetric(object):
    def __init__(self, **kwargs):
        self._value = None
        self.name = kwargs.get('name')
        self.source = kwargs.get('source')
        self.last_update = None
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if value == self._value:
            return
        old = self._value
        self._value = value
        self.source.on_metric_value_changed(metric=self, now=self.last_update, value=value, old=old)
    def update_needed(self, *args, **kwargs):
        now = kwargs.get('now')
        if now is None:
            now = time.time()
        last_update = self.last_update
        if last_update is None:
            return True
        return now - last_update >= self.source.update_interval
    def update(self, *args, **kwargs):
        now = kwargs.get('now')
        if now is None:
            now = time.time()
            kwargs.setdefault('now', now)
        last_update = self.last_update
        self.last_update = now
        kwargs.setdefault('last_update', last_update)
        self.do_update(*args, **kwargs)
    def do_update(self, *args, **kwargs):
        pass
    def get_conf_data(self):
        return dict(cls_name=self.__class__.__name__, name=self.name)
