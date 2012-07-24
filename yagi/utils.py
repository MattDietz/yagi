import fcntl
import socket
import struct
import sys


def import_class(klass_str):
    module, sep, klass = klass_str.rpartition('.')
    try:
        __import__(module)
        return getattr(sys.modules[module], klass)
    except (ImportError, ValueError, AttributeError):
        raise Exception("Could not load class %s" % klass_str)


def import_module(mod_str):
    try:
        __import__(mod_str)
        return sys.modules[mod_str]
    except (ImportError, ValueError, AttributeError):
        raise Exception("Could not load module %s" % mod_str)


def get_ip_addr():
    """Try to get a default. Override if this isn't your default NIC"""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def addr_by_iface(iface):
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', 'eth0'))[20:24])
    ifaces = ['eth0', 'en0']
    for iface in ifaces:
        try:
            return addr_by_iface(iface)
        except Exception:
            pass
    return '127.0.0.1'
