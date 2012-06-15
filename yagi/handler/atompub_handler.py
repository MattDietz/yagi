import time

import httplib2

import yagi.auth
import yagi.config
import yagi.handler
import yagi.log
import yagi.serializer.atom

with yagi.config.defaults_for("atompub") as default:
    default("auth_key", "key")
    default("auth_user", "user")
    default("url", "http://127.0.0.1/nova")
    default("retries", "5")
    default("max_wait", "600")
    default("interval", "30")

LOG = yagi.log.logger


class MessageDeliveryFailed(Exception): pass


class AtomPub(yagi.handler.BaseHandler):
    CONFIG_SECTION = "atompub"

    def _topic_url(self, key):
        url = self.config_get("url")
        return url % dict(event_type=key)

    def _send_notification(self, endpoint, puburl, headers, body, conn):
        LOG.info("Sending message to %s with body: %s" % (endpoint, body))
        headers = {"Content-Type": "application/atom+xml"}
        try:
            resp, content = conn.request(endpoint, "POST",
                                         body=body,
                                         headers=headers)
            if resp.status != 201:
                msg = ("AtomPub resource create failed for %s Status: "
                            "%s, %s" % (puburl, resp.status, content) )
                raise Exception(msg)
        except Exception, e:
            msg = ("AtomPub Delivery Failed to %s with:\n%s" % (endpoint, e))
            raise MessageDeliveryFailed(msg)

    def new_http_connection(force=False):
        conn = httplib2.Http()
        auth_method = yagi.auth.get_auth_method()
        headers = {}
        if auth_method:
            auth_method(conn, headers, force=force)
        else:
            raise Exception("Invalid auth or no auth supplied")
        return conn, headers

    def handle_messages(self, notifications):
        interval = self.config_get("interval")
        max_wait = self.config_get("max_wait")
        conn, headers = self.new_http_connection()

        for notification in notifications:
            payload = notification.payload
            try:
                entity = dict(content=payload,
                              id=payload["message_id"],
                              event_type=payload["event_type"])
                payload_body = yagi.serializer.atom.dump_item(entity)
            except KeyError, e:
                LOG.error("Malformed Notification: %s" % payload)
                LOG.exception(e)
                continue

            conn.follow_all_redirects = True
            puburl = self._topic_url(payload["event_type"])
            LOG.debug("ATOM Pub post to: %s *******\n%s\n=======" % (puburl,
                                                                payload_body))
            endpoint = self._topic_url(payload["event_type"])
            tries = 1
            while True:
                try:
                    self._send_notification(endpoint, puburl, headers,
                                            payload_body, conn)
                    notification.ack()
                    break
                except MessageDeliveryFailed, e:
                    # Re-auth and try again
                    tries += 1
                    wait = min(tries*interval, max_wait)
                    time.sleep(wait)
                    conn, headers = self.new_http_connection(force=True)
                    LOG.exception(e)
                    continue

