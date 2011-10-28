import unittest

import httplib2
import stubout
import webob

import yagi.config
import yagi.notifier.atompub

class MockResponse(object):
    def __init__(self, status_code=200):
        self.status = status_code

class AtomPubTests(unittest.TestCase):
    """Tests to ensure the ATOM Pub code holds together as expected"""

    def setUp(self):
        self.stubs = stubout.StubOutForTesting()
        config_dict = {
            'atompub': {
                'url' : 'http://127.0.0.1:9000/test/%(event_type)s',
                'user': 'user',
                'key': 'key',
            },
            'event_feed': {
                'feed_title': 'feed_title',
                'feed_host': 'feed_host',
                'use_https': False,
                'port': 'port'
            }
        }

    def tearDown(self):
        self.stubs.UnsetAll()

    def test_notify(self):
        messages = [
            { 'event_type': 'instance_create',
              'id': 1,
              'content': dict(a=3) }
        ]
        self.called = False
        def mock_request(*args, **kwargs):
            self.called = True
            return MockResponse(201), None

        self.stubs.Set(httplib2.Http, 'request', mock_request)
        yagi.notifier.atompub.notify(messages)
        self.assertEqual(self.called, True)

    def test_notify_fails(self):
        messages = [
            { 'event_type': 'instance_create',
              'id': 1,
              'content': dict(a=3) }
        ]
        self.called = False
        def mock_request(*args, **kwargs):
            self.called = True
            return MockResponse(404), None

        self.stubs.Set(httplib2.Http, 'request', mock_request)
        yagi.notifier.atompub.notify(messages)
        self.assertEqual(self.called, True)
