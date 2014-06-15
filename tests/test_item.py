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
from wikidataeditor.item import Item


class TestClient(unittest.TestCase):

    def setUp(self):
        self.ua = 'MyTool/0.1'
        self.site = Site(self.ua)
        self.item = Item(self.site, 'Q1000')

    def test_entity_id_normalization(self):
        item1 = Item(self.site, 'Q1000')
        item2 = Item(self.site, '1000')
        item3 = Item(self.site, 1000)

        assert item1.entity == 'Q1000'
        assert item2.entity == 'Q1000'
        assert item3.entity == 'Q1000'


if __name__ == '__main__':
    unittest.main()
