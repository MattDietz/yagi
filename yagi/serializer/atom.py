import fcntl
import json
import socket
import struct

import feedgenerator

import yagi.config
import yagi.utils


def _entity_link(entity_id, key):
    return unicode(''.join([_entity_url(), '%s/' % key, str(entity_id)]))


def _entity_url():
    conf = yagi.config.config_with('event_feed')
    feed_host = conf('feed_host')
    scheme = "%s://" % (conf('use_https') or 'http')
    port = conf('port') or ''
    if len(port) > 0:
        port = ':%s' % port

    if not feed_host:
        feed_host = yagi.utils.get_ip_addr()
    return unicode(''.join([scheme, feed_host, port, '/']))


def write_items(self, handler):
    for item in self.items:
        handler.startElement(u"entry", self.item_attributes(item))
        self.add_item_elements(handler, item)
        handler.addQuickElement(u"content", json.dumps(item['contents']),
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
            title=unicode(entity['event_type']),
            link=_entity_link(entity['id'], entity['event_type']),
            description=unicode(entity['event_type']),
            contents=entity['content'])
    return feed.writeString('utf-8')
