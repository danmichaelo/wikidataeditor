import json
import logging
import time

logger = logging.getLogger('wikidataeditor.item')


class Item:

    def __init__(self, site, entity):
        """
        site    : reference to a wikidataeditor.Site
        entity  : Q number of the item as a string,
                  with or without the initial 'Q'
        """
        self.site = site

        # Normalize
        self.entity = 'Q{}'.format('{}'.format(entity).lstrip('Q'))

        self.props = self.get_props('labels|descriptions|aliases|sitelinks')
        self.exists = True
        if self.props is None:
            self.exists = False

    def prop(self, prop, language, fallback_languages=None):
        if prop not in self.props:
            return None

        res = self.props[prop]
        languages = [language]
        if fallback_languages:
            languages.extend(fallback_languages)

        for lang in languages:
            if lang in res:
                if 'value' in res[lang]:
                    return res[lang]['value']
                elif 'title' in res[lang]:
                    return res[lang]['title']
                else:
                    return [r['value'] for r in res[lang]]
        return None

    def label(self, language, fallback_languages=None):
        return self.prop('labels', language, fallback_languages)

    def description(self, language, fallback_languages=None):
        return self.prop('descriptions', language, fallback_languages)

    def aliases(self, language, fallback_languages=None):
        return self.prop('aliases', language, fallback_languages)

    def sitelinks(self, site_id):
        return self.prop('sitelinks', site_id)

    def pageinfo(self):
        args = {
            'action': 'query',
            'prop': 'info',
            'intoken': 'edit',
            'titles': self.entity
        }
        return self.site.raw_api_call(args)

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
        return self.site.raw_api_call(args)

    def claims(self, prop):
        args = {
            'action': 'wbgetclaims',
            'entity': self.entity,
            'property': prop
        }
        resp = self.site.raw_api_call(args)
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
        response = self.site.raw_api_call(args)
        return response['claim']

    def create_claim_if_not_exists(self, prop, value):

        claims = self.claims(prop)

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

        response = self.site.raw_api_call(args)
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

        response = self.site.raw_api_call(args)
        return response

    def remove_label(self, lang, summary=None):
        return self.set_label(lang, '', summary)

    def get_props(self, props='labels|descriptions|aliases|sitelinks', languages=None):
        args = {
            'action': 'wbgetentities',
            'props': props,
            'ids': self.entity
        }

        if languages:
            args['languages'] = languages

        result = self.site.raw_api_call(args)

        if result['success'] != 1:
            return None
        return result['entities'][self.entity]
