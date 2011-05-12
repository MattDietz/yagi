import fcntl
import socket
import struct

import feedgenerator

import yagi.config
import yagi.utils


def _entity_link(entity_id):
    return unicode(''.join([_entity_url(), 'event/', str(entity_id)]))


def _entity_url():
    feed_host = yagi.config.get('event_feed', 'feed_host')
    scheme = "%s://" % (yagi.config.get('event_feed', 'use_https') or 'http')
    port = yagi.config.get('event_feed', 'port') or ''
    if len(port) > 0:
        port = ':%s' % port

    if not feed_host:
        feed_host = yagi.utils.get_ip_addr()
    return unicode(''.join([scheme, feed_host, port, '/']))


def write_items(self, handler):
    for item in self.items:
        handler.startElement(u"entry", self.item_attributes(item))
        self.add_item_elements(handler, item)
        handler.addQuickElement(u"content", item['payload'],
                dict(type='application/json'))
        handler.endElement(u"entry")


def dumps(entities):
    """Serializes a list of dictionaries as an ATOM feed"""

    # Horrible hack to get it to care about content elements
    feedgenerator.Atom1Feed.write_items = write_items

    title = unicode(yagi.config.get('event_feed', 'feed_title'))
    feed = feedgenerator.Atom1Feed(
        title=title,
        link=_entity_url(),
        feed_url=_entity_url(),
        description=title,
        language=u'en')
    for entity in entities:
        feed.add_item(
            title=unicode(entity['klass']),
            link=_entity_link(entity['id']),
            description=unicode(entity['klass']),
            contents=entity['content'])
    return feed.writeString('utf-8')
