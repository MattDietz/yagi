import httplib2

import yagi.config
import yagi.log
import yagi.serializer.atom

with yagi.config.defaults_for('atompub') as default:
    pass

LOG = yagi.log.logger


def topic_url(key):
    url = yagi.config.get('atompub', 'url') or 'http://127.0.0.1/%(event_type)s'
    return url % dict(event_type=key)

def notify(notifications):
    auth_user = yagi.config.get('atompub', 'user', default=None)
    auth_key = yagi.config.get('atompub', 'key', default=None)
    conn = httplib2.Http()
    if auth_user and auth_key:
        conn.add_credentials(auth_user, auth_key)
    for notification in notifications:
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
        puburl = topic_url(notification['event_type'])
        LOG.debug('ATOM Pub post to: %s *******\n%s\n=======' % (puburl, notification_body))
        try:
            endpoint = topic_url(notification['event_type'])
            LOG.info('Sending message to %s' % endpoint)
            resp, content = conn.request(endpoint, 'POST',
                                     body=notification_body, headers=headers)
            if resp.status != 201:
                LOG.error('ATOM Pub resource create failed for %s Status: %s, %s' % (puburl, resp.status, content) )

        except Exception, e:
            LOG.error('Error sending notification to ATOM Pub resource%s\n\n%s'
                     % (endpoint, e))
