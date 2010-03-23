# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.brightcove.testing
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.cp.testing
import zope.component
import zope.security.management
import zope.site.hooks


def create_content(root):
    old_site = zope.site.hooks.getSite()
    zope.site.hooks.setSite(root)
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)

    for i in range(3):
        name = 'c%s' % (i + 1)
        c = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        c.teaserTitle = c.shortTeaserTitle = u'%s teaser' % name
        repository[name] = c

    zope.site.hooks.setSite(old_site)


CPBrightcoveZCMLLLayer = zeit.cms.testing.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting-av.zcml'),
    __name__,
    'CPBrightcoveLayer',
    product_config=(zeit.brightcove.testing.product_config +
                    zeit.content.cp.testing.product_config),
    allow_teardown=True)


class CPBrightcoveLayer(zeit.brightcove.testing.BrightcoveHTTPLayer,
                      CPBrightcoveZCMLLLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'autopilot.txt',
        'cpextra.txt',
        'fullgraphical.txt',
        'quiz.txt',
        'teaser.txt',
        'teaser-two-column-layout.txt',
        'teaserbar.txt',
        'xml.txt',
        ))
    av_test = zeit.content.cp.testing.FunctionalDocFileSuite(
        'av.txt',
        layer=CPBrightcoveLayer)
    suite.addTest(av_test)
    rss_test = zeit.content.cp.testing.FunctionalDocFileSuite(
        'rss.txt',
        layer=zeit.content.cp.testing.FeedServer)
    return suite
