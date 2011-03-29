import feedgenerator

import yagi.config


def _entity_link(entity_id):
    return unicode(''.join([_entity_url(), 'event/', str(entity_id)]))

def _entity_url():
    feed_link = yagi.config.get('atom_serializer', 'feed_base_url')
    return unicode(''.join(['https://', feed_link, '/']))
    

def dumps(entities):
    """Serializes a list of dictionaries as an ATOM feed"""
    title = unicode(yagi.config.get('atom_serializer', 'feed_title')) 
    feed = feedgenerator.Atom1Feed(
        title = title,
        link = _entity_url(),
        feed_url = _entity_url(),
        description = title,
        language = u'en'
        )
    for entity in entities:
        feed.add_item(
            title = unicode(entity['klass']),
            link = _entity_link(entity['id']),
            description = unicode(entity['klass'])
        )
    return feed.writeString('utf-8')
