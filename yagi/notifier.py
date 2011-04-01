import pubsubhubbub_publish

import yagi.config
import yagi.log

LOG = yagi.log.logger


def notify(*urls):
    host = yagi.config.get('hub', 'host')
    port = yagi.config.get('hub', 'port', default='80')
    scheme = yagi.config.get('hub', 'use_https') == True and 'https' or 'http'
    hub_url = "%s://%s:%s" % (scheme, host, port)
    try:
        LOG.debug('Publishing to %s' % hub_url)
        pubsubhubbub_publish.publish(hub_url, *urls)
        LOG.debug('Message published')
    except pubsubhubbub_publish.PublishError, e:
        LOG.debug('Publish failed %s' % e)
