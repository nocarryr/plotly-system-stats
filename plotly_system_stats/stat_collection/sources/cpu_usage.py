import time
import threading

import psutil

from plotly_system_stats.stat_collection.sources.base_source import BaseSource, BaseMetric

class CPUPercentThread(threading.Thread):
    def __init__(self, **kwargs):
        super(CPUPercentThread, self).__init__()
        self.percpu = kwargs.get('percpu')
        self.callback = kwargs.get('callback')
    def run(self):
        v = psutil.cpu_percent(interval=1, percpu=self.percpu)
        self.callback(thread=self, value=v)
        
class CPUUsage(BaseSource):
    def __init__(self, **kwargs):
        self._cpu_percent_threads = {'total':None, 'percpu':None}
        self._cpu_percent_values = {'total':None, 'percpu':None}
        self._last_now = None
        kwargs.setdefault('name', 'CPU Usage')
        super(CPUUsage, self).__init__(**kwargs)
        self.add_metric(CPUMetric, name='Total')
        cpu_count = psutil.cpu_count()
        if cpu_count > 1:
            for i in range(cpu_count):
                self.add_metric(CPUMetric, name='CPU%s' % (i), index=i)
    def get_cpu_percent(self):
        t_dict = self._cpu_percent_threads
        cb = self.on_cpu_percent_thread_done
        for key, percpu in {'total':False, 'percpu':True}.iteritems():
            t = t_dict.get(key)
            if t is not None and t.is_alive():
                continue
            t = CPUPercentThread(percpu=percpu, callback=cb)
            self._cpu_percent_threads[key] = t
            t.start()
    def on_cpu_percent_thread_done(self, **kwargs):
        t = kwargs.get('thread')
        value = kwargs.get('value')
        if t.percpu:
            key = 'percpu'
        else:
            key = 'total'
        self._cpu_percent_threads[key] = None
        self._cpu_percent_values[key] = value
        if None in self._cpu_percent_values.values():
            return
        cpu_percent = self._cpu_percent_values.copy()
        self._cpu_percent_values.update({'total':None, 'percpu':None})
        self.update_metrics(cpu_percent=cpu_percent, now=self._last_now)
    def update_metrics(self, *args, **kwargs):
        now = kwargs.get('now')
        if now is None:
            now = time.time()
            kwargs.setdefault('now', now)
        self._last_now = now
        cpu_percent = kwargs.get('cpu_percent')
        if cpu_percent is None:
            self.get_cpu_percent()
            return
        super(CPUUsage, self).update_metrics(*args, **kwargs)
    @classmethod
    def build_defaults(cls):
        return [dict(cls=cls)]
    
class CPUMetric(BaseMetric):
    def __init__(self, **kwargs):
        super(CPUMetric, self).__init__(**kwargs)
        self.index = kwargs.get('index')
    def do_update(self, *args, **kwargs):
        cpu_percent = kwargs.get('cpu_percent')
        if self.index is None:
            self.value = cpu_percent['total']
        else:
            self.value = cpu_percent['percpu'][self.index]
