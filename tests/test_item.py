import unittest
import sys
import os
import httpretty
from sure import expect
import requests
import simplejson as json

mypath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, mypath + '/../')

from wikidataeditor import Site
from wikidataeditor.item import Item


class TestClient(unittest.TestCase):

    def setUp(self):
        ua = 'MyTool/0.1'
        site = Site(ua)
        self.item = Item(site, 'Q1000')

    def test_initialization(self):
        assert self.item.entity == '1000'


if __name__ == '__main__':
    unittest.main()
