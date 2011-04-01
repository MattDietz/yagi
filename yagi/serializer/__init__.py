import yagi.config
import yagi.utils


def feed_serializer():
    serializer = yagi.utils.import_module(yagi.config.get('event_feed',
            'serializer_driver'))
    return serializer
