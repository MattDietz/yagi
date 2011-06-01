import urlparse

import eventlet
from eventlet import wsgi
import routes
import routes.middleware
import webob
import webob.dec

import yagi.config
import yagi.log
import yagi.persistence
import yagi.serializer

LOG = yagi.log.logger


class EventFeed(object):
    def __init__(self):
        self.db_driver = yagi.persistence.persistence_driver()
        self.feed_serializer = yagi.serializer.feed_serializer()

    @webob.dec.wsgify()
    def route_request(self, req):
        path = req.environ['PATH_INFO'][1:].split('/')
        resource = path[0]
        path = filter(lambda x: len(x) > 0, path)
        if len(path) > 2:
            raise Exception("Invalid resource")
        if len(path) == 2:
            index = path[1]
            return self.get_one(req, resource, index)
        elif len(resource) > 0:
            return self.get_all_of_resource(req, resource)
        return self.get_all(req)

    def get_one(self, req, resource, uuid):
        LOG.debug('get_one %s %s' % (resource, uuid))
        elements = self.db_driver.get(resource, uuid)
        return self.respond(req, elements)

    def get_all_of_resource(self, req, resource):
        LOG.debug('get_all_of_resource %s' % resource)
        elements = self.db_driver.get_all_of_type(resource)
        print elements
        return self.respond(req, elements)

    def get_all(self, req):
        LOG.debug('get_all')
        elements = self.db_driver.get_all()
        return self.respond(req, elements)

    def respond(self, req, elements):
        response = webob.Response()
        response.content_type = 'application/atom+xml'
        response.body = self.feed_serializer.dumps(elements)
        return response

    def listen(self, port):
        wsgi.server(eventlet.listen(('', port)), self.route_request)


def start():
    port = int(yagi.config.get('event_feed', 'port'))
    LOG.debug('Starting feed on port %d' % port)
    event_feed = EventFeed()
    event_feed.listen(port)
