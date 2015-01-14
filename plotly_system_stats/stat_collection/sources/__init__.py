from net_io import NetworkDevice
from cpu_usage import CPUUsage

_SOURCE_CLASSES = [NetworkDevice, CPUUsage]
SOURCE_CLASSES = dict(zip([cls.__name__ for cls in _SOURCE_CLASSES], _SOURCE_CLASSES))
