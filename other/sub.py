import sys
from urllib import urlencode

try:
    import httplib2
except ImportError, e:
    print "httplib2 not found. Please install it before attempting "\
          "to continue."
    sys.exit(1)


def send_subscribe(argv):
    """
    Usage:

    python sub.py <topic url> <callback url> <hub url>

    Example:

    python sub.py http://1.2.3.4/compute.run_instance http://2.3.4.5:8000 \
                  http://2.3.4.5:8080
    """

    req = httplib2.Http()
    topic = argv[1]
    callback = argv[2]
    hub = argv[3]
    form_data = {
            'hub.mode': 'subscribe',
            'hub.topic': topic,
            'hub.callback': callback,
            'hub.verify': 'sync'
            }
    res, content = req.request(hub, 'POST',
            urlencode(form_data))
    print content


send_subscribe(sys.argv)
