# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import stabledict
import zc.sourcefactory.basic
import zeit.cms.content.sources
import zope.dottedname.resolve


class CPTypeSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-types-url'
    attribute = 'name'


class CPExtraSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-extra-url'
    attribute = 'id'

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for element in tree.iterchildren():
            for_ = zope.dottedname.resolve.resolve(element.get('for'))
            if for_.providedBy(context.__parent__):
                result.append(unicode(element.get('id')))
        return result


class RSSTimeFormatSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = stabledict.StableDict([
        ('none', _('None')), # default
        ('date', _('Date')),
        ('time', _('Time')),
        ])

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]
