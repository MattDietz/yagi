import feedgenerator


def dumps(entities):
    """Serializes a list of dictionaries as an ATOM feed"""
    feed = feedgenerator.Atom1Feed(
        title = u'some title',
        link = u'http://127.0.0.1',
        feed_url = u'http://127.0.0.1',
        description = u'Notification Feed',
        language = u'en'
        )
    for entity in entities:
        feed.add_item(
            title = entity['id'],
            link = 'http://127.0.0.1?id=%s' % entity['id'],
            description = entity['klass']
        )
    return feed.writeString('utf-8')
