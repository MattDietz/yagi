import sys

def import_class(klass_str):
    module, sep, klass = klass_str.rpartition('.')
    try:
        __import__(module)
        return getattr(sys.modules[module], klass)
    except (ImportError, ValueError, AttributeError), exc:
        print exc
        raise Exception, "Could not load class %s" % klass_str
