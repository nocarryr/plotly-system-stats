import os
import json


class Config(object):
    def __init__(self, **kwargs):
        self.data = {}
        self.conf_loader = JSONConfLoader()
        self.data.update(self.conf_loader.read_all())
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value
        self.conf_loader.write_item(key, value)
    def update(self, d):
        self.data.update(d)
        self.conf_loader.write_all(self.data)
    
class BaseConfLoader(object):
    def __init__(self, **kwargs):
        pass
    def write_item(self, key, value):
        pass
    def read_item(self, key):
        pass
    def write_all(self, data):
        pass
    def read_all(self):
        pass
    
class FileBasedLoader(BaseConfLoader):
    _file_extension = None
    _default_path = '~/.plotly_system_stats'
    def __init__(self, **kwargs):
        filename = kwargs.get('filename')
        if filename is None:
            ext = self._file_extension
            filename = self._default_path
            if ext is not None:
                filename = '.'.join([filename, ext])
        self.filename = os.path.expanduser(filename)
    def write_file(self, s):
        with open(self.filename, 'w') as f:
            f.write(s)
    def read_file(self):
        if not os.path.exists(self.filename):
            return None
        with open(self.filename, 'r') as f:
            s = f.read()
        return s
        
class JSONConfLoader(FileBasedLoader):
    def write_item(self, key, value):
        d = self.read_all()
        if d.get(key) == value:
            return
        d[key] = value
        self.write_all(d)
    def read_item(self, key):
        d = self.read_all()
        return d.get(key)
    def write_all(self, data):
        s = json.dumps(data, indent=3)
        self.write_file(s)
    def read_all(self):
        s = self.read_file()
        if s is None:
            return {}
        return json.loads(s)
        
