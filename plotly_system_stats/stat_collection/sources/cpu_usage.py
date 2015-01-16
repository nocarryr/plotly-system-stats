import time
import threading

import psutil

from plotly_system_stats.stat_collection.sources.base_source import BaseSource, BaseMetric

class CPUPercentThread(threading.Thread):
    def __init__(self, **kwargs):
        super(CPUPercentThread, self).__init__()
        self.percpu = kwargs.get('percpu')
        self.callback = kwargs.get('callback')
        self.now = kwargs.get('now')
    def run(self):
        v = psutil.cpu_percent(interval=1, percpu=self.percpu)
        self.callback(thread=self, value=v, now=self.now)
        
class CPUUsage(BaseSource):
    def __init__(self, **kwargs):
        self._cpu_percent_thread = None
        self._last_now = None
        super(CPUUsage, self).__init__(**kwargs)
        if self.name == 'CPU Total':
            self.add_metric(CPUMetric, name='Percent')
        else:
            cpu_count = psutil.cpu_count()
            for i in range(cpu_count):
                self.add_metric(CPUMetric, name='CPU%s' % (i), index=i)
    def get_cpu_percent(self):
        cb = self.on_cpu_percent_thread_done
        if self.name == 'CPU Total':
            percpu = False
        else:
            percpu = True
        t = self._cpu_percent_thread = CPUPercentThread(percpu=percpu, callback=cb)
        t.start()
    def on_cpu_percent_thread_done(self, **kwargs):
        value = kwargs.get('value')
        self._cpu_percent_thread = None
        self.update_metrics(cpu_percent=value, now=self._last_now)
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
        return [dict(cls=cls, name='CPU Total'), 
                dict(cls=cls, name='CPU Cores')]
    
class CPUMetric(BaseMetric):
    def __init__(self, **kwargs):
        super(CPUMetric, self).__init__(**kwargs)
        self.index = kwargs.get('index')
    def do_update(self, *args, **kwargs):
        cpu_percent = kwargs.get('cpu_percent')
        if self.index is None:
            self.value = cpu_percent
        else:
            self.value = cpu_percent[self.index]
