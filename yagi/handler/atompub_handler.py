import yagi.handler
import httplib2

import yagi.config
import yagi.log
import yagi.serializer.atom

with yagi.config.defaults_for('atompub') as default:
    default("auth_key", 'key')
    default("auth_user", 'user')
    default("url", 'http://127.0.0.1/nova')
    default("retries", "5")

LOG = yagi.log.logger


class MessageDeliveryFailed(Exception): pass


class AtomPub(yagi.handler.BaseHandler):
    CONFIG_SECTION = "atompub"

    def _topic_url(self, key):
        url = self.config_get('url')
        return url % dict(event_type=key)

    def _send_notification(self, endpoint, puburl, body, conn):
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

    def handle_messages(self, notifications):
        auth_user = self.config_get('user', default=None)
        auth_key = self.config_get('key', default=None)
        conn = httplib2.Http()
        if auth_user and auth_key:
            conn.add_credentials(auth_user, auth_key)

        for notification in notifications:
            try:
                entity = dict(content=notification,
                              id=notification['message_id'],
                              event_type=notification['event_type'])
                notification_body = yagi.serializer.atom.dump_item(entity)
            except KeyError, e:
                LOG.error('Malformed Notification: %s' % notification)
                LOG.exception(e)
                continue

            conn.follow_all_redirects = True
            puburl = self._topic_url(notification['event_type'])
            LOG.debug('ATOM Pub post to: %s *******\n%s\n=======' % (puburl,
                                                                notification_body))
            endpoint = self._topic_url(notification['event_type'])
            for i in xrange(int(self.config_get('retries'))):
                try:
                    self._send_notification(endpoint, puburl, notification_body, conn)
                    break
                except MessageDeliveryFailed, e:
                    LOG.exception(e)
                    continue

