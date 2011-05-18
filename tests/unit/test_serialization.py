import unittest

import stubout

import yagi.config
import yagi.serializer


class SerializerTests(unittest.TestCase):
    def setUp(self):
        self.stubs = stubout.StubOutForTesting()

    def tearDown(self):
        self.stubs.UnsetAll()

    def test_load_serializer(self):
        """Contrived test for basic functionality"""

        def config_get(*args, **kwargs):
            return 'yagi.serializer.atom'

        self.stubs.Set(yagi.config, 'get', config_get)

        ser = yagi.serializer.feed_serializer()
        self.assertEqual(ser, yagi.serializer.atom)
