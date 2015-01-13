import time
from collections import OrderedDict

class BaseSource(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        if not hasattr(self, 'update_interval'):
            self.update_interval = kwargs.get('update_interval', 4.)
        self.value_change_callback = kwargs.get('value_change_callback')
        self.metrics = OrderedDict()
    def add_metric(self, cls, **kwargs):
        kwargs.setdefault('source', self)
        obj = cls(**kwargs)
        self.metrics[obj.name] = obj
        return obj
    def update_metrics(self, *args, **kwargs):
        for obj in self.metrics.itervalues():
            obj.update(*args, **kwargs)
    def on_metric_value_changed(self, **kwargs):
        cb = self.value_change_callback
        if cb is None:
            return
        kwargs.setdefault('source', self)
        cb(**kwargs)
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
        self.source.on_metric_value_changed(metric=self, value=value, old=old)
    def update(self, *args, **kwargs):
        now = time.time()
        last_update = self.last_update
        if last_update is not None:
            if now - last_update < self.source.update_interval:
                return
        self.last_update = now
        kwargs.setdefault('now', now)
        kwargs.setdefault('last_update', last_update)
        self.do_update(*args, **kwargs)
    def do_update(self, *args, **kwargs):
        pass
    def get_conf_data(self):
        return dict(cls_name=self.__class__.__name__, name=self.name)
