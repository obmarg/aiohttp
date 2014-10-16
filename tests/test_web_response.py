import unittest
from unittest import mock
from aiohttp.web import Request, StreamResponse
from aiohttp.protocol import Request as RequestImpl, HttpVersion


class TestStreamResponse(unittest.TestCase):

    def make_request(self, method, path, headers=()):
        self.app = mock.Mock()
        self.transport = mock.Mock()
        message = RequestImpl(self.transport, method, path)
        message.headers.extend(headers)
        self.payload = mock.Mock()
        self.protocol = mock.Mock()
        req = Request(self.app, message, self.payload, self.protocol)
        return req

    def test_ctor(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        self.assertEqual(req, resp._request)
        self.assertIsNone(req._response)
        self.assertEqual(200, resp.status_code)
        self.assertTrue(resp.keep_alive)
        self.assertEqual(HttpVersion(1, 1), resp.version)

    def test_status_code_cannot_assign_nonint(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        with self.assertRaises(TypeError):
            resp.status_code = 'abc'
        self.assertEqual(200, resp.status_code)

    def test_status_code_setter(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        resp.status_code = 300
        self.assertEqual(300, resp.status_code)

    def test_status_code_cannot_assing_after_sending_headers(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        resp.send_headers()
        with self.assertRaises(RuntimeError):
            resp.status_code = 300
        self.assertEqual(200, resp.status_code)

    def test_change_version(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        resp.version = HttpVersion(1, 0)
        self.assertEqual(HttpVersion(1, 0), resp.version)

    def test_change_version_bad_type(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        with self.assertRaises(TypeError):
            resp.version = 123
        self.assertEqual(HttpVersion(1, 1), resp.version)

    def test_cannot_change_version_after_sending_headers(self):
        req = self.make_request('GET', '/')
        resp = StreamResponse(req)

        resp.send_headers()
        with self.assertRaises(RuntimeError):
            resp.version = HttpVersion(1, 0)
        self.assertEqual(HttpVersion(1, 1), resp.version)