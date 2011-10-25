import httplib2

import yagi.config
import yagi.log
import yagi.serializer.atom

with yagi.config.defaults_for('atompub') as default:
    default("auth_key", 'key')
    default("auth_user", 'user')
    default("url", 'http://127.0.0.1/foo')
    default("retries", "5")

LOG = yagi.log.logger


class MessageDeliveryFailed(Exception): pass


def topic_url(key):
    url = yagi.config.get('atompub', 'url') or \
            'http://127.0.0.1/%(event_type)s'
    return url % dict(event_type=key)


def _send_notification(endpoint, puburl, body, conn):
    LOG.info('Sending message to %s with body: %s' % (endpoint, body))
    headers = {'Content-Type': 'application/atom+xml'}
    try:
        resp, content = conn.request(endpoint, 'POST',
                                     body=body,
                                     headers=headers)
        if resp.status != 201:
            msg = ('AtomPub resource create failed for %s Status: '
                        '%s, %s' % (puburl, resp.status, content) )
            raise Exception(msg)
    except Exception, e:
        msg = ('AtomPub Deliver Failed with:\n%s' % e)
        raise MessageDeliveryFailed(msg)


def notify(notifications):
    auth_user = yagi.config.get('atompub', 'user', default=None)
    auth_key = yagi.config.get('atompub', 'key', default=None)
    conn = httplib2.Http()
    if auth_user and auth_key:
        conn.add_credentials(auth_user, auth_key)

    for notification in notifications:
        entity = dict(content=notification,
                      id=notification['id'],
                      event_type=notification['event_type'])
        notification_body = yagi.serializer.atom.dump_item(entity)

        conn.follow_all_redirects = True
        puburl = topic_url(notification['event_type'])
        LOG.debug('ATOM Pub post to: %s *******\n%s\n=======' % (puburl,
                                                            notification_body))
        endpoint = topic_url(notification['event_type'])
        for i in xrange(yagi.config.get('atompub', 'retries')):
            try:
                _send_notification(endpoint, puburl, notification_body, conn)
                break
            except MessageDeliveryFailed, e:
                LOG.exception(e)
                continue
