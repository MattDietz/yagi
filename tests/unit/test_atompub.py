import unittest

import httplib2
import stubout
import webob

import yagi.notifier.atompub
from yagi.tests.unit import fake

class MockResponse(object):
    def __init__(self, status_code=200):
        self.status = status

class AtomPubTests(unittest.TestCase):
    """Tests to ensure the ATOM Pub code holds together as expected"""

    def setUp(self):
        self.stubs = stubout.StubOutForTesting()

    def tearDown(self):
        self.stubs.UnsetAll()

    def test_notify(self):
        messages = [1,2,3,4,5]
        self.called = False
        def mock_request(*args, **kwargs):
            self.called = True
            return MockResponse(201), None

        self.stubs.Set(httplib2.Http, 'request', mock_request)
        yagi.notifier.atompub.notify(messages)
        self.assertEqual(self.called, True)

    def test_notify_fails(self):
        messages = [1,2,3,4,5]
        self.called = False
        def mock_request(*args, **kwargs):
            self.called = True
            return MockResponse(404), None

        self.stubs.Set(httplib2.Http, 'request', mock_request)
        yagi.notifier.atompub.notify(messages)
        self.assertEqual(self.called, True)
