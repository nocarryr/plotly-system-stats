import weakref

class WeakCallbacks(object):
    def __init__(self):
        self.instance_methods = weakref.WeakValueDictionary()
        self.unbound_funcs = weakref.WeakSet()
    def bind(self, cb):
        if hasattr(cb, 'im_self'):
            obj_id = id(cb.im_self)
            wr_key = (cb.im_func, obj_id)
            self.instance_methods[wr_key] = cb.im_self
        else:
            self.unbound_funcs.add(cb)
    def unbind(self, cb):
        if hasattr(cb, 'im_self'):
            obj_id = id(cb.im_self)
            wr_key = (cb.im_func, obj_id)
            if wr_key in self.instance_methods:
                del self.instance_methods[wr_key]
        else:
            self.unbound_funcs.discard(cb)
    def __call__(self, *args, **kwargs):
        for key in self.instance_methods.keys()[:]:
            f, obj_id = key
            obj = self.instance_methods.get(key)
            if obj is None:
                continue
            f(obj, *args, **kwargs)
        for f in self.unbound_funcs:
            f(*args, **kwargs)
    
