# Yagi

A PubSubHubBub Publisher implementation in Python

## Why PubSubHubBub?

We wanted to use a defined spec with easy to use clients, and PubSubHubBub fit
the bill nicely. 

## Why implement an external publisher?

The original impetus for this project is to adapt an existing piece of
software to sending notifications without laying the job of managing those
notifications on said implementation. Because PubSubHubBub requires an ATOM
feed, we didn\'t want the original software from having to worry about
completely unrelated functionality. Additionally, this route buys us a
lot of flexibility.

## Dependencies:

* argparse
* feedgenerator
* httplib2
* redis
* webob
* eventlet
* daemon
* pubsubhubbub_publish (available under the publisher_clients folder after checking out the project from [Google Code](http://code.google.com/p/pubsubhubbub/source/checkout) NOTE: the plan is to replace this dependency later with our implementation
* carrot (if using Rabbit)
* routes

## Setting up the hub

Download the Google App Engine SDK for Linux and add it to your path

    http://code.google.com/appengine/downloads.html

Then checkout the reference hub.

    svn checkout http://pubsubhubbub.googlecode.com/svn/trunk/ pubsubhubbub-read-only

Install pubsubhubbub_publisher for python

    cd pubsubhubbub-read-only/publisher_clients/python
    sudo python setup.py install

Start the hub

    cd pubsubhubbub-read-only
    dev_appserver.py hub/ -p<port number specified in yagi.conf>

## Setting up Yagi

After setting up the hub, above

    cd yagi
    cp yagi.conf.default yagi.conf
    # edit yagi.conf, setting up as appropriate
    # Take care to update the feed_host variable in the event_feed
    # section as it will be the IP address presented in the feed. Otherwise
    # Yagi will attempt to infer it, and it doesn't seem to be all that
    # successful at it.
    sudo cp yagi.conf /etc
    sudo python setup.py install
    yagi-event
    yagi-feed

## Testing subscriptions

    cd yagi

    # You'll want to run this in multiple screen windows or terminal sessions, as the callback process
    # won't daemonize

    python subscriber/callback.py <sub_port>
    python subscriber/sub.py <topic> <callback> <hub>

    # I usually load other/push_rabbit.py in an iPython session
    cd other
    ipython
    import push_rabbit

    # the cast below is assuming you setting up yagi to listen on a queue named 'notifications.warn'
    push_rabbit.cast(dict(a=3), 'instance', 'notifications', 'warn')

You should see XML content being pushed to your window running callback.py, above.
