import unittest
import sys
import os
import httpretty
# from sure import expect
import requests
import simplejson as json

mypath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, mypath + '/../')

from wikidataeditor import Site


class TestClient(unittest.TestCase):

    def setUp(self):
        ua = 'MyTool/0.1'
        self.site = Site(ua)

    def test_initialization(self):
        ua = 'MyTool/0.2'
        api_url = 'http://my-custom-site.org/api'
        self.site = Site(ua, api_url)
        assert self.site.user_agent == ua
        assert self.site.api_url == api_url

    @httpretty.activate
    def test_login_failed(self):

        response = {'login': {'result': 'NotExists'}}
        httpretty.register_uri(httpretty.POST, self.site.api_url,
                               content_type="application/json",
                               body=json.dumps(response))

        stat = self.site.login('me', 'secret')
        assert stat is False

    @httpretty.activate
    def test_login_ok(self):

        def request_callback(request, uri, headers):

            token = 'b5780b6e2f27e20b450921d9461010b4'
            login_token = '4db760e273b413549a32ba4eb06d08db'
            cookieprefix = 'enwiki'
            sessionid = '17ab96bd8ffbe8ca58a78657a918558e'

            if request.body.find(token) != -1:
                body = {'login': {
                    'result': 'Success',
                    'token': login_token,
                    'cookieprefix': cookieprefix,
                    'sessionid': sessionid
                }}
            else:
                body = {'login': {
                    'result': 'NeedToken',
                    'token': token,
                    'cookieprefix': cookieprefix,
                    'sessionid': sessionid
                }}
            return (200, headers, json.dumps(body))

        httpretty.register_uri(httpretty.POST, self.site.api_url,
                               content_type='application/json',
                               body=request_callback)

        stat = self.site.login('me', 'secret')

        assert stat is True


if __name__ == '__main__':
    unittest.main()
