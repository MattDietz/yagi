import urlparse
import sys

import eventlet
import eventlet.wsgi

import webob.dec

pool = eventlet.GreenPool()

@webob.dec.wsgify
def callback(req):
    query_string = req.environ.get('QUERY_STRING')
    if query_string:
        query_dict = urlparse.parse_qs(req.environ['QUERY_STRING'])
        print query_dict
        return query_dict['hub.challenge'][0]
    print "\n\nGot request:\n"
    print "Req.environ %s " % req.environ
    print "Req.body %s " % req.body



eventlet.wsgi.server(eventlet.listen(('', int(sys.argv[1]))), callback,
        custom_pool=pool)
