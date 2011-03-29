import yagi.config
import yagi.utils

def feed_serializer():
    conf = yagi.config.parse_conf()
    serializer = yagi.utils.import_module(conf.get('event_feed',
            'serializer_driver'))
    return serializer
    
