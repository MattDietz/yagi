import unittest

import stubout
import webob

import yagi.feed.feed


class FeedTests(unittest.TestCase):
    """Some lame tests to hold everything together until I can write a better
    router in"""

    def setUp(self):
        self.stubs = stubout.StubOutForTesting()

        def mock_fun(*args):
            pass
        self.stubs.Set(yagi.feed.feed.EventFeed, '__init__', mock_fun)
        self.stubs.Set(yagi.feed.feed.EventFeed, 'respond', mock_fun)

    def tearDown(self):
        self.stubs.UnsetAll()

    def test_get_one(self):
        self.called = False

        def mock_get_one(*args):
            self.called = True
        self.stubs.Set(yagi.feed.feed.EventFeed, 'get_one', mock_get_one)
        feed = yagi.feed.feed.EventFeed()
        req = webob.Request.blank('/dummy/0')
        req.get_response(feed.route_request)
        self.assertEqual(self.called, True)

    def test_get_all(self):
        self.called = False

        def mock_get_all(*args):
            self.called = True
        self.stubs.Set(yagi.feed.feed.EventFeed, 'get_all', mock_get_all)
        feed = yagi.feed.feed.EventFeed()
        req = webob.Request.blank('/')
        req.get_response(feed.route_request)
        self.assertEqual(self.called, True)

    def test_get_all_of_resource(self):
        self.called = False

        def mock_get_all(*args):
            pass

        def mock_get(*args):
            self.called = True

        self.stubs.Set(yagi.feed.feed.EventFeed, 'get_all', mock_get_all)
        self.stubs.Set(yagi.feed.feed.EventFeed, 'get_all_of_resource',
                mock_get)
        feed = yagi.feed.feed.EventFeed()
        req = webob.Request.blank('/instance')
        req.get_response(feed.route_request)
        self.assertEqual(self.called, True)

    def test_get_all_of_resource_2(self):
        self.called = False

        def mock_get_all(*args):
            pass

        def mock_get(*args):
            self.called = True

        self.stubs.Set(yagi.feed.feed.EventFeed, 'get_all', mock_get_all)
        self.stubs.Set(yagi.feed.feed.EventFeed, 'get_all_of_resource',
                mock_get)
        feed = yagi.feed.feed.EventFeed()
        # Trailing slash
        req = webob.Request.blank('/instance/')
        req.get_response(feed.route_request)
        self.assertEqual(self.called, True)
