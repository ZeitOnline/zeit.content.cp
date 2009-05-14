# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import __future__
import pkg_resources
import re
import zeit.cms.testing
import zope.testing.doctest
import zope.testing.renormalizing

product_config = {
    'zeit.content.cp': {
        'rules-url': 'file://%s' % pkg_resources.resource_filename(
            'zeit.content.cp.tests', 'rule_testdata.py'),
        'rss-folder': 'rss',
        'feed-update-minimum-age': 30,
    }}



layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'zeit.content.cp.tests.layer', allow_teardown=True)


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),
    (re.compile('0x[0-9a-f]+'), "0x..."),
    (re.compile('[0-9a-f]{32}'), "<MD5>"),
    (re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(\+[0-9]{2}:[0-9]{2})?'),
     "<ISO DATE>"),
    (re.compile('[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} [+-][0-9]{4}'),
     "<RFC822 DATE>"),
])


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('checker', checker)
    kw.setdefault('layer', layer)
    kw.setdefault('product_config', product_config)
    kw.setdefault('globs', dict(with_statement=__future__.with_statement))
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = layer
    product_config = product_config
