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
    use_https = yagi.config.get_bool('event_feed', 'use_https')
    scheme = "%s://" % ('https' if use_https else 'http')
    port = conf('port') or ''
    if len(port) > 0:
        port = ':%s' % port

    if not feed_host:
        feed_host = yagi.utils.get_ip_addr()
    return unicode(''.join([scheme, feed_host, port, '/']))


class PagedFeed(feedgenerator.Atom1Feed):

    # Get it to care about content elements
    def write_items(self, handler):
        for item in self.items:
            handler.startElement(u"entry", self.item_attributes(item))
            self.add_item_elements(handler, item)
            handler.addQuickElement(u"content", json.dumps(item['contents']),
                    dict(type='application/json'))
            handler.endElement(u"entry")

    def add_root_elements(self, handler):
        super(PagedFeed, self).add_root_elements(handler)
        if self.feed.get('next_page_url') is not None:
            handler.addQuickElement(u"link",
                                    "",
                                    {u"rel": u"next",
                                     u"href": self.feed['next_page_url']})
        if self.feed.get('previous_page_url') is not None:
            handler.addQuickElement(u"link",
                                    "",
                                    {u"rel": u"previous",
                                     u"href": self.feed['previous_page_url']})


def dumps(entities, previous_page=None, next_page=None):
    """Serializes a list of dictionaries as an ATOM feed"""

    title = unicode(yagi.config.get('event_feed', 'feed_title'))
    feed = PagedFeed(
        title=title,
        link=_entity_url(),
        feed_url=_entity_url(),
        description=title,
        language=u'en',
        previous_page_url=("%s?page=%s" % (_entity_url(), previous_page)) \
                          if previous_page is not None else None,
        next_page_url=("%s?page=%s" % (_entity_url(), next_page)) \
                          if next_page is not None else None)
    for entity in entities:
        feed.add_item(
            title=unicode(entity['event_type']),
            link=_entity_link(entity['id'], entity['event_type']),
            description=unicode(entity['event_type']),
            contents=entity['content'])
    return feed.writeString('utf-8')
