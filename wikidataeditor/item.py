import simplejson as json


class Item:

    def __init__(self, site, entity):
        """
        site    : reference to a wikidataeditor.Site
        entity  : Q number of the item as a string,
                  with or without the initial 'Q'
        """
        self.site = site

        # Make sure it's a string, then strip off 'Q'
        self.entity = '{}'.format(entity).lstrip('Q')

    def pageinfo(self):
        args = {
            'action': 'query',
            'prop': 'info',
            'intoken': 'edit',
            'titles': self.entity
        }
        return self.raw_api_call(args)

    def set_reference(self, claim, reference):
        """
        Add a reference (snak) to a claim unless an *exactly*
        similar reference already exists. Note that only a minor
        modification will cause the reference to be re-added.
        """

        # logger.debug(json.dumps(claim, indent='\t'))

        statement = claim['id']
        if 'references' in claim:
            for ref in claim['references']:
                if ref['snaks'] == reference:
                    logger.info('  Reference already exists')
                    return

        logger.info('  Adding reference')
        time.sleep(2)

        response = self.pageinfo()
        itm = response['query']['pages'].items()[0][1]
        baserevid = itm['lastrevid']
        edittoken = itm['edittoken']

        args = {
            'action': 'wbsetreference',
            'bot': 1,
            'statement': statement,
            'snaks': json.dumps(reference),
            'token': edittoken,
            'baserevid': baserevid
        }
        return self.raw_api_call(args)

    def claims(self, prop):
        args = {
            'action': 'wbgetclaims',
            'entity': self.entity,
            'property': prop
        }
        resp = self.raw_api_call(args)
        if 'claims' in resp and prop in resp['claims']:
            return resp['claims'][prop]
        return []

    def create_claim(self, prop, value):

        response = self.pageinfo()
        itm = response['query']['pages'].items()[0][1]
        baserevid = itm['lastrevid']
        edittoken = itm['edittoken']

        args = {
            'action': 'wbcreateclaim',
            'bot': 1,
            'entity': self.entity,
            'property': prop,
            'snaktype': 'value',
            'value': json.dumps(value),
            'token': edittoken,
            'baserevid': baserevid
        }

        logger.info('  %s: Adding claim %s = %s', self.entity, prop, value)
        time.sleep(2)
        response = self.raw_api_call(args)
        return response['claim']

    def create_claim_if_not_exists(self, prop, value):

        claims = self.get_claims(prop)

        if claims:
            current_value = claims[0]['mainsnak']['datavalue']['value']
            if value == current_value:
                logger.info('  Claim %s already exists with the same value %s',
                            prop, value)
                return claims[0]
            else:
                logger.warn('  Claim %s already exists. ' +
                            'Existing value: %s, new value: %s',
                            prop, current_value, value)
            return None

        return self.create_claim(prop, value)

    def set_description(self, lang, value, summary=None):

        response = self.pageinfo()
        itm = response['query']['pages'].items()[0][1]
        baserevid = itm['lastrevid']
        edittoken = itm['edittoken']

        args = {
            'action': 'wbsetdescription',
            'bot': 1,
            'id': self.entity,
            'language': lang,
            'value': value,
            'token': edittoken
        }

        if summary:
            args['summary'] = summary

        logger.info(args)

        logger.info('  Setting description')
        time.sleep(2)

        response = self.raw_api_call(args)
        return response

    def remove_description(self, lang, summary=None):
        return self.set_description(lang, '', summary)

    def set_label(self, lang, value, summary=None):

        response = self.pageinfo()
        itm = response['query']['pages'].items()[0][1]
        baserevid = itm['lastrevid']
        edittoken = itm['edittoken']

        args = {
            'action': 'wbsetlabel',
            'bot': 1,
            'id': self.entity,
            'language': lang,
            'value': value,
            'token': edittoken
        }

        if summary:
            args['summary'] = summary

        logger.info(args)

        logger.info('  Setting label')
        time.sleep(2)

        response = self.raw_api_call(args)
        return response

    def remove_label(self, lang, summary=None):
        return self.set_label(lang, '', summary)

    def get_props(self, props='labels|descriptions|aliases', languages=None):
        args = {
            'action': 'wbgetentities',
            'props': props,
            'ids': self.entity
        }

        if languages:
            args['languages'] = languages

        result = self.raw_api_call(args)

        if result['success'] != 1:
            return None
        return result['entities'][self.entity]
