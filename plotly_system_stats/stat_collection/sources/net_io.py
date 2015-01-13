import os

from plotly_system_stats.stat_collection.sources.base_source import BaseSource, BaseMetric

class NetworkDevice(BaseSource):
    def __init__(self, **kwargs):
        super(NetworkDevice, self).__init__(**kwargs)
        self.device_name = kwargs.get('device_name')
        for key in ['rx', 'tx']:
            self.add_metric(NetworkIOCurrent, name=key)
    @classmethod
    def build_defaults(cls):
        l = []
        for dev in os.listdir('/sys/class/net'):
            if dev == 'lo':
                continue
            l.append(dict(cls=cls, name=dev, device_name=dev))
        return l
    def get_conf_data(self):
        d = super(NetworkDevice, self).get_conf_data()
        d['device_name'] = self.device_name
        return d
        
class NetworkIOMetric(BaseMetric):
    _stats_file_fmt = '/sys/class/net/%(name)s/statistics/%(io_type)s_bytes'
    def get_total_bytes(self):
        d = dict(name=self.source.device_name, io_type=self.name)
        fn = self._stats_file_fmt % d
        with open(fn, 'r') as f:
            s = f.read()
        return int(s)
    
class NetworkIOTotal(NetworkIOMetric):
    def do_update(self, *args, **kwargs):
        self.value = self.get_total_bytes()
        
class NetworkIOCurrent(NetworkIOMetric):
    def __init__(self, **kwargs):
        super(NetworkIOCurrent, self).__init__(**kwargs)
        self.total_bytes = None
    def do_update(self, *args, **kwargs):
        current_total = self.get_total_bytes()
        last_total = self.total_bytes
        self.total_bytes = current_total
        if last_total is None:
            return
        self.value = current_total - last_total
