# encoding=utf8
# @author Dan Michael O. Heggø <danmichaelo@gmail.com>
__ver__ = '0.0.1'

import requests
import logging
import time
import re
import simplejson as json

from item import Item

logger = logging.getLogger('wikidataeditor')


class Site:

    def __init__(self, user_agent,
                 api_url='https://www.wikidata.org/w/api.php'):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

        self.api_url = api_url

        # Respect https://www.mediawiki.org/wiki/Maxlag
        lps = r'Waiting for [^ ]*: (?P<lag>[0-9.]+) seconds? lagged'
        self.lagpattern = re.compile(lps)

    @property
    def user_agent(self):
        return self.session.headers.get('User-Agent')

    def raw_api_call(self, args):
        while True:
            url = self.api_url
            args['format'] = 'json'
            args['maxlag'] = 5
            # print args

            # for k, v in args.iteritems():
            #     if type(v) == unicode:
            #         args[k] = v.encode('utf-8')
            #     else:
            #         args[k] = v

            # data = urllib.urlencode(args)
            logger.debug(args)
            response = self.session.post(url, data=args)
            response = json.loads(response.text)

            logger.debug(response)

            if 'error' not in response:
                return response

            code = response['error'].pop('code', 'Unknown')
            info = response['error'].pop('info', '')
            if code == 'maxlag':
                lag = self.lagpattern.search(info)
                if lag:
                    logger.warn('Pausing due to database lag: %s', info)
                    time.sleep(int(lag.group('lag')))
                    continue

            logger.error("Unknown API error: %s\n%s\nResponse:\n%s",
                         info,
                         json.dumps(args, indent="\t"),
                         json.dumps(response, indent="\t"))
            return response
            # sys.exit(1)

    def login(self, user, pwd):
        args = {
            'action': 'login',
            'lgname': user,
            'lgpassword': pwd
        }
        response = self.raw_api_call(args)
        if response['login']['result'] == 'NeedToken':
            args['lgtoken'] = response['login']['token']
            response = self.raw_api_call(args)

        return (response['login']['result'] == 'Success')

    def item(self, entity):
        return Item(self, entity)

    def pageinfo(self, entity):
        args = {
            'action': 'query',
            'prop': 'info',
            'intoken': 'edit',
            'titles': entity
        }
        return self.raw_api_call(args)

    def get_entities(self, site, page):
        args = {
            'action': 'wbgetentities',
            'sites': site,
            'titles': page
        }
        return self.raw_api_call(args)

    def add_entity(self, site, lang, title):
        args = {
            'new': 'item',
            'data': {
                'sitelinks': {site: {'site': site, 'title': title}},
                'labels': {lang: {'language': lang, 'value': title}}
            }
        }

        logger.info('  Adding entity for %s:%s', site, title)
        time.sleep(3)

        return self.edit_entity(**args)

    def edit_entity(self, data={}, site=None, title=None, new=None,
                    summary=None):

        response = self.pageinfo('DUMMY')
        itm = response['query']['pages'].items()[0][1]
        edittoken = itm['edittoken']

        args = {
            'action': 'wbeditentity',
            'bot': 1,
            'data': json.dumps(data),
            'token': edittoken
        }
        if site:
            args['site'] = site

        if title:
            args['title'] = title

        if new:
            args['new'] = new

        if summary:
            args['summary'] = summary

        response = self.raw_api_call(args)
        return response
