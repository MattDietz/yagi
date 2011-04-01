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

* feedgenerator
* redis
* webob
* eventlet
* daemon
* pubsubhubbub_publish (available under the publisher_clients folder after checking out the project from [Google Code](http://code.google.com/p/pubsubhubbub/source/checkout) 
* carrot (if using Rabbit)
