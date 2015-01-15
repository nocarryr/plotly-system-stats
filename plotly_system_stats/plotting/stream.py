import time
import threading

from plotly.plotly import Stream as plStream

from plotly_system_stats.plotting.plot_config import plot_config

class StreamIDError(Exception):
    def __str__(self):
        return 'Not enough stream ids available'

class PlotlyStreamContextError(Exception):
    def __init__(self, stream):
        self.msg = 'Stream %r must be open before writing' % (stream)
    def __str__(self):
        return repr(self.msg)
        
class Stream(object):
    def __init__(self, **kwargs):
        self._trace = None
        self.trace_id = None
        stream_id = kwargs.get('stream_id')
        if stream_id is None:
            stream_id = plot_config.get_available_stream_id()
            if stream_id is None:
                raise StreamIDError()
        self.stream_id = stream_id
        self.trace = kwargs.get('trace')
        self._stream = None
        self._last_write = None
        self._disconnect_timer = None
    @property
    def trace(self):
        return self._trace
    @trace.setter
    def trace(self, value):
        if value == self._trace:
            return
        self._trace = value
        if value is None:
            self.trace_id = None
        else:
            self.trace_id = '///'.join([value.plot.id, value.id])
        self.set_conf('trace_id', self.trace_id)
    @property
    def stream(self):
        s = self._stream
        if s is None or s.exited:
            s = self._stream = StreamIO(self)
        return s
    def get_conf(self, key, default=None):
        d = plot_config.get('streams', {}).get(self.stream_id)
        return d.get(key, default)
    def set_conf(self, key, item):
        d = plot_config.get('streams').get(self.stream_id)
        if d is None:
            d = {}
            plot_config.get('streams')[self.stream_id] = d
        d[key] = item
        plot_config.write_all()
    def _rebuild_disconnect_timer(self):
        self._last_write = time.now()
        t = self._disconnect_timer
        if t is not None and t.is_alive():
            t.cancel()
        t = self._disconnect_timer = threading.Timer(30., self._disconnect_timer_cb)
        t.start()
    def _disconnect_timer_cb(self):
        s = self._stream
        s.needs_close = True
        self._disconnect_timer = None
    def write(self, data):
        s = self.stream
        with s:
            s.write(data)
        
class StreamIO(object):
    def __init__(self, stream):
        self.stream = stream
        self.pl_stream = None
        self.is_open = False
        self.needs_close = False
        self.exited = False
        self._entry_count = 0
    def write(self, data):
        if not self.is_open:
            raise PlotlyStreamContextError(self.stream)
        self.pl_stream.write(data)
    def __enter__(self):
        self._entry_count += 1
        if self.is_open:
            return
        if self.pl_stream is None:
            self.pl_stream = plStream(self.stream.stream_id)
        self.pl_stream.open()
        self.is_open = True
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._entry_count -= 1
        if self._entry_count > 0:
            return
        if self.is_open and self.needs_close:
            self.pl_stream.close()
            self.is_open = False
