from net_io import NetworkDevice

_SOURCE_CLASSES = [NetworkDevice]
SOURCE_CLASSES = dict(zip([cls.__name__ for cls in _SOURCE_CLASSES], _SOURCE_CLASSES))
