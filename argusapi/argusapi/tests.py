import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'argusapi')
    def test_table(self):
        from .views import table
        request = testing.DummyRequest()
        request.matchdict['table'] = 'IP'
        data = table(request)
        self.assertEqual(data, {'a': 'b'})
    def test_tables(self):
        from .views import tables
        request = testing.DummyRequest()
        data = tables(request)
        self.assertEqual(data, {'a': 'b'})
