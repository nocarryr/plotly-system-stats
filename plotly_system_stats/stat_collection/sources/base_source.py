import time
from collections import OrderedDict

from plotly_system_stats.config import config
from plotly_system_stats.utils import WeakCallbacks

GROUPS_BY_NAME = {}
GROUPS_BY_INDEX = {}

class SourceGroup(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.index = self.get_conf('index')
        if self.index is None:
            self.index = kwargs.get('index')
            if self.index is None:
                if not len(GROUPS_BY_INDEX):
                    self.index = 0
                else:
                    self.index = max(GROUPS_BY_INDEX.keys()) + 1
            self.set_conf('index', self.index)
        if self.get_conf('name') is None:
            self.set_conf('name', self.name)
        self.source_names = self.get_conf('source_names', [])
        self.sources = {}
        GROUPS_BY_INDEX[self.index] = self
        GROUPS_BY_NAME[self.name] = self
    def get_conf(self, key, default=None):
        return config.get('source_groups', {}).get(key, default)
    def set_conf(self, key, item):
        source_groups = config.get('source_groups')
        if source_groups is None:
            source_groups = {}
            config.set('source_groups', source_groups)
        d = source_groups.get(self.name)
        if d is None:
            d = {}
            source_groups[self.name] = d
        d[key] = item
        config.write_all()
    def add_source(self, source):
        if source.name not in self.source_names:
            self.source_names.append(source.name)
            self.set_conf('source_names', self.source_names)
        i = self.source_names.index(source.name)
        self.sources[i] = source
        source.group = self
        
class BaseSource(object):
    def __init__(self, **kwargs):
        self._group = None
        self._group_name = None
        self.name = kwargs.get('name')
        if hasattr(self.__class__, '_group_name'):
            self.group_name = self.__class__._group_name
        else:
            self.group_name = kwargs.get('group_name')
        if not hasattr(self, 'update_interval'):
            self.update_interval = kwargs.get('update_interval', 4.)
        self.value_change_callbacks = WeakCallbacks()
        self.metrics = OrderedDict()
    @property
    def group_name(self):
        return self._group_name
    @group_name.setter
    def group_name(self, value):
        if value == self._group_name:
            return
        self._group_name = value
        if value is not None:
            group = GROUPS_BY_NAME.get(value)
            if group is None:
                group = self.build_group(name=value)
        else:
            group = None
        self.group = group
    @property
    def group(self):
        return self._group
    @group.setter
    def group(self, value):
        if self._group == value:
            return
        self._group = value
        if value is None:
            return
        if self._group_name != value.name:
            self._group_name = value.name
        value.add_source(self)
    def build_group(self, **kwargs):
        if hasattr(self, 'group_index'):
            kwargs.setdefault('index', self.group_index)
        return SourceGroup(**kwargs)
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
