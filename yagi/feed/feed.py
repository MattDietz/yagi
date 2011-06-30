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

with yagi.config.defaults_for('event_feed') as default:
    default('pagesize', '1000')


class EventFeed(object):
    def __init__(self):
        self.db_driver = yagi.persistence.persistence_driver()
        self.feed_serializer = yagi.serializer.feed_serializer()
        self.pagesize = int(yagi.config.get('event_feed', 'pagesize'))

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

    def _get_page(self, req, key=None):
        maxpage = self.db_driver.pages(self.pagesize,
                                     self.db_driver.count(key)) - 1
        if 'page' in req.str_params:
            return (int(req.str_params['page']), maxpage)
        else:
            return (maxpage, maxpage)

    def get_one(self, req, resource, uuid):
        LOG.debug('get_one %s %s' % (resource, uuid))
        elements = self.db_driver.get(resource, uuid)
        return self.respond(req, elements)

    def get_all_of_resource(self, req, resource):
        LOG.debug('get_all_of_resource %s' % resource)
        page, maxpage = self._get_page(req, resource)
        elements = self.db_driver.get_all_of_type(resource,
                                                  self.pagesize,
                                                  page)
        #print elements
        return self.respond(req, elements, page, maxpage)

    def get_all(self, req):
        LOG.debug('get_all')
        page, maxpage = self._get_page(req)
        elements = self.db_driver.get_all(self.pagesize, page)
        return self.respond(req, elements, page, maxpage)

    def respond(self, req, elements, page, maxpage):
        response = webob.Response()
        response.content_type = 'application/atom+xml'
        previous_page = next_page = None
        if page > 0:
            previous_page = page - 1
        if page < maxpage:
            next_page = page + 1
        response.body = self.feed_serializer.dumps(elements,
                                                   previous_page=previous_page,
                                                   next_page=next_page)
        return response

    def listen(self, port):
        wsgi.server(eventlet.listen(('', port)), self.route_request)


def start():
    port = int(yagi.config.get('event_feed', 'port'))
    LOG.debug('Starting feed on port %d' % port)
    event_feed = EventFeed()
    event_feed.listen(port)
