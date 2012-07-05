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


def _categories():
        conf = yagi.config.config_with('event_feed')
        val = 'atom_categories'
        return [c.strip() for c in
                (conf(val).split(',') if conf(val) else [])]


def clean_content(cdict):
    return dict([i for i in cdict.items() if not i[0].startswith('_')])


class PagedFeed(feedgenerator.Atom1Feed):

    # Get it to care about content elements
    def write_items(self, handler):
        for item in self.items:
            self.write_item(handler, item)

    # Get it to care about content elements
    def write_item(self, handler, item, root=False):
        handler.startElement(u"entry",
                             self.root_attributes() if root else {})
        self.add_item_elements(handler, item)
        handler.addQuickElement(u"content",
                json.dumps(clean_content(item['contents'])),
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
        event_type=unicode(entity['event_type'])
        feed.add_item(
            title=unicode(entity['event_type']),
            link=_entity_link(entity['id'], entity['event_type']),
            description=event_type,
            contents=entity['content'],
            categories=[event_type] + _categories())
    return feed.writeString('utf-8')


def dump_item(entity):
    """Serializes a single dictionary as an ATOM entry"""
    from StringIO import StringIO

    outfile = StringIO()
    handler = feedgenerator.SimplerXMLGenerator(outfile, 'utf-8')
    handler.startDocument()
    title = unicode(yagi.config.get('event_feed', 'feed_title'))
    feed = PagedFeed(
        title=title,
        link=_entity_url(),
        feed_url=_entity_url(),
        description=title,
        language=u'en',
        previous_page_url=None,
        next_page_url=None)

    event_type=unicode(entity['event_type'])
    feed.add_item(title=unicode(entity['event_type']),
                link=_entity_link(entity['id'], entity['event_type']),
                description=event_type,
                contents=entity['content'],
                categories=[event_type] + _categories())
    feed.write_item(handler, feed.items[0], root=True)
    return outfile.getvalue()
