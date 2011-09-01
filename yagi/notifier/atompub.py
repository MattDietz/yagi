import httplib2

import yagi.config
import yagi.log
import yagi.serializer.atom

with yagi.config.defaults_for('atompub') as default:
    pass

LOG = yagi.log.logger


def topic_url(key):
    host = yagi.config.get('atompub', 'host') or '127.0.0.1'
    port = yagi.config.get('atompub', 'port', default=80)
    if yagi.config.get_bool('atompub', 'use_https'):
        scheme = 'https'
    else:
        scheme = 'http'
    return '%s://%s:%s/%s' % (scheme, host, port, key)


def notify(notifications):
    auth_user = yagi.config.get('atompub', 'user', default=None)
    auth_key = yagi.config.get('atompub', 'key', default=None)
    conn = httplib2.Http()
    if auth_user and auth_key:
        conn.add_credentials(auth_user, auth_key)
    for notification in notifications:
        yagi.serializer.atom.dumps(notifications)

        # TODO(mdietz): This is a semi-hack to make the notifications look
        # the way the # serializer expects them to look. Move this later
        # to utils
        formatted_notification = dict(id=notification['message_id'],
                                      event_type=notification['event_type'],
                                      content=notification)

        notification_body = yagi.serializer.atom.dumps(
                                            [formatted_notification])
        headers = {'Content-Type': 'application/atom+xml'}
        conn.follow_all_redirects = True
        try:
            resp, content = conn.request(topic_url(notification['event_type']),
                    'POST', body=notification_body, headers=headers)
            if resp.status != 201:
                LOG.error('ATOM Pub resource create failed for %s' % topic_url)

        except Exception, e:
            LOG.error('Error sending notification to ATOM Pub resource%s\n\n%s'
                     % (topic_url, e))
            raise
