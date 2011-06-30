import pubsubhubbub_publish

import yagi.config
import yagi.log

with yagi.config.defaults_for('hub') as default:
    default('host', '127.0.0.1')
    default('port', '8000')

LOG = yagi.log.logger


def topic_url(key):
    host = yagi.config.get('event_feed', 'feed_host') or '127.0.0.1'
    port = yagi.config.get('event_feed', 'port', default=80)
    if yagi.config.get_bool('event_feed', 'use_https'):
        scheme = 'https'
    else:
        scheme = 'http'
    return '%s://%s:%s/%s' % (scheme, host, port, key)


def hub_url():
    host = yagi.config.get('hub', 'host')
    port = yagi.config.get('hub', 'port', default='80')
    scheme = 'https' if yagi.config.get_bool('hub', 'use_https') else 'http'
    return "%s://%s:%s" % (scheme, host, port)


def notify(notifications):
    host = hub_url()
    topics = {}
    # Compile the list of updated topic urls
    for notification in notifications:
        event_type = notification['event_type']
        if not event_type in topics:
            topics[event_type] = topic_url(event_type)

    for event_type, topic in topics.iteritems():
        try:
            LOG.debug('Publishing topic %s to %s' % (topic, host))
            pubsubhubbub_publish.publish(host, topic)
        except pubsubhubbub_publish.PublishError, e:
            LOG.debug('Publish failed %s' % e)
