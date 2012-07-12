import pubsubhubbub_publish

import yagi.config
import yagi.handler
import yagi.log


with yagi.config.defaults_for('hub') as default:
    default('host', '127.0.0.1')
    default('port', '8000')

LOG = yagi.log.logger


class PubSubHubBubHandler(yagi.handler.BaseHandler):
    CONFIG_SECTION = "hub"

    def _topic_url(self, key):
        host = yagi.config.get('event_feed', 'feed_host') or '127.0.0.1'
        port = yagi.config.get('event_feed', 'port', default=80)
        if yagi.config.get_bool('event_feed', 'use_https'):
            scheme = 'https'
        else:
            scheme = 'http'
        return '%s://%s:%s/%s' % (scheme, host, port, key)

    def _hub_url(self):
        host = self.config_get('host')
        port = self.config_get('port', default='80')
        scheme = 'https' if self.config_getbool('use_https') else 'http'
        return "%s://%s:%s" % (scheme, host, port)

    def _notify(self, notifications):
        host = self._hub_url()
        topics = {}
        # Compile the list of updated topic urls
        for notification in notifications:
            payload = notification.payload
            try:
                event_type = payload['event_type']
                if not event_type in topics:
                    topics[event_type] = self._topic_url(event_type)
            except KeyError, e:
                LOG.error('Malformed Notification: %s' % payload)
                LOG.exception(e)

        for event_type, topic in topics.iteritems():
            try:
                LOG.info('Publishing topic %s to %s' % (topic, host))
                pubsubhubbub_publish.publish(host, topic)
                notification.ack()
            except pubsubhubbub_publish.PublishError, e:
                LOG.exception('Publish failed:\n%s' % e)
