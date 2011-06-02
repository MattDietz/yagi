import sys
from urllib import urlencode

import httplib2

def send_subscribe(argv):
    req = httplib2.Http()
    topic_port = argv[1]
    hub_port = argv[2]
    sub_port = argv[3]
    topic = argv[4]
    form_data = { 
            'hub.mode': 'subscribe', 
            'hub.topic':'http://127.0.0.1:%/%s' % (topic_port, topic),
            'hub.callback': 'http://127.0.0.1:%s' % hub_port,
            'hub.verify': 'sync'
            }
    res, content = req.request('http://127.0.0.1:%s' % sub_port, 'POST',
            urlencode(form_data))
    print content


send_subscribe(sys.argv)
