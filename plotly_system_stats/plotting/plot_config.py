import plotly.tools as pl_tools

from plotly_system_stats.config import config
    
def build_config():
    d = {}
    d = dict(
        all_stream_ids=[], 
        streams={}, 
        figures={}, 
        plots={}, 
    )
    config.set('plotly', d)
    
    
if config.get('plotly') is None:
    build_config()

class PlotConfig(object):
    @property
    def data(self):
        return config.get('plotly')
    def write_all(self):
        config.write_all()
    def set(self, key, item):
        self.data[key] = item
        config.write_all()
    def get(self, key, default=None):
        return self.data.get(key, default)
    def update(self, d):
        self.data.update(d)
        config.write_all()
    def refresh_stream_ids(self):
        changed = False
        stream_ids = pl_tools.get_credentials_file()['stream_ids']
        for stream_id in stream_ids:
            if stream_id in self.data['all_stream_ids']:
                continue
            self.data['all_stream_ids'].append(stream_id)
            changed = True
        if changed:
            self.write_all()
    def get_available_stream_id(self):
        self.refresh_stream_ids()
        for stream_id in self.data['all_stream_ids']:
            if stream_id in self.data['streams']:
                continue
            return stream_id
        return None
        
plot_config = PlotConfig()
    
