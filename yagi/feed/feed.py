import eventlet
from eventlet import wsgi
import routes
import webob
import webob.dec

import yagi.config
import yagi.log
import yagi.persistence
import yagi.serializer

LOG = yagi.log.logger

@webob.dec.wsgify()
def event_feed(req):
    db_driver = yagi.persistence.persistence_driver()
    feed_serializer = yagi.serializer.feed_serializer()
    elements = db_driver.get_all('events')

    response = webob.Response()
    response.content_type = 'application/atom+xml'
    response.body = feed_serializer.dumps(elements)

    return response

def start():
    port = int(yagi.config.get('event_feed', 'port'))
    LOG.debug('Starting feed on port %d' % port) 
    wsgi.server(eventlet.listen(('', port)), event_feed)
