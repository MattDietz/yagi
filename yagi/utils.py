import sys

def import_class(klass_str):
    module, sep, klass = klass_str.rpartition('.')
    try:
        __import__(module)
        return getattr(sys.modules[module], klass)
    except (ImportError, ValueError, AttributeError), exc:
        raise Exception, "Could not load class %s" % klass_str

def import_module(mod_str):
    try:
        __import__(mod_str)
        return sys.modules[mod_str]
    except (ImportError, ValueError, AttributeError), exc:
        raise Exception, "Could not load module %s" % mod_str
