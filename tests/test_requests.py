from mock import patch
from unittest import TestCase

from pyneric.requests import METHOD_METHODS, RequestHandler


@patch('pyneric.requests.requests.request')
class RequestHandlerTestCase(TestCase):

    def test_method_methods(self, request_mock):
        handler = RequestHandler()
        url = object()
        for method, defaults in METHOD_METHODS.items():
            kwargs = dict(defaults or {}, method=method, url=url)
            getattr(handler, method)(url)
            request_mock.assert_called_once_with(**kwargs)
            request_mock.reset_mock()

    def test_alter_kwargs(self, request_mock):
        class Handler(RequestHandler):

            def _alter_kwargs(self, kwargs):
                kwargs.pop('invalid', None)
                kwargs.update(method='meth')
                return super(Handler, self)._alter_kwargs(kwargs)

        handler = Handler()
        url = object()
        headers = object()
        kwargs = dict(method='meth', url=url, headers=headers)
        handler.request('post', url, invalid=object(), headers=headers)
        request_mock.assert_called_once_with(**kwargs)
        request_mock.reset_mock()
        handler.get(url, headers=headers)
        kwargs.update(METHOD_METHODS['get'] or {})
        request_mock.assert_called_once_with(**kwargs)

    def test_request(self, request_mock):
        class Handler(RequestHandler):

            def __init__(self, request_result):
                self._request_result = request_result

            def request(self, **kwargs):
                if kwargs.pop('_call_super', False):
                    super(Handler, self).request(**kwargs)
                return self._request_result

        kwargs = dict(method='post', url=object())
        expected = object()
        handler = Handler(expected)
        self.assertEqual(expected, handler.request(**kwargs))
        self.assertEqual(0, request_mock.call_count)
        self.assertEqual(expected, handler.request(_call_super=True, **kwargs))
        request_mock.assert_called_once_with(**kwargs)

    def test_request_handlers(self, request_mock):
        class Handler(RequestHandler):

            def __init__(self):
                self.calls = 0

            def request(self, **kwargs):
                self.calls += 1
                return super(Handler, self).request(**kwargs)

        handler = Handler()
        kwargs = dict(method=object(), url=object())
        handler.request(_handlers=(handler, handler), **kwargs)
        request_mock.assert_called_once_with(**kwargs)
        self.assertEqual(3, handler.calls)
