# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import rwproperty
import zeit.content.cp.block
import zeit.content.cp.interfaces
import zope.container.interfaces
import zope.interface
import lxml.objectify
import lxml.etree

class XMLBlock(zeit.content.cp.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IXMLBlock,
        zope.container.interfaces.IContained)

    type = 'xmlblock'


XMLBlockFactory = zeit.content.cp.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    XMLBlock, 'xmlblock', _('Raw XML block'))