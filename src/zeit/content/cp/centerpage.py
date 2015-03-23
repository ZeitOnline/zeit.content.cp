# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.redirect.interfaces import IRenameInfo
from zeit.connector.search import SearchVar
from zeit.content.cp.interfaces import TEASER_ID_NAMESPACE
import UserDict
import collections
import copy
import grokcore.component as grok
import itertools
import lxml.etree
import pkg_resources
import xml.sax.saxutils
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.related.related
import zeit.cms.sitecontrol.interfaces
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.cp.interfaces
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.proxy


class CenterPage(zeit.cms.content.metadata.CommonMetadata,
                 UserDict.DictMixin):

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = pkg_resources.resource_string(__name__,
                                                     'cp-template.xml')
    editable_areas = collections.OrderedDict([
        ('lead', lxml.etree.XPath('cluster/region[@area="lead"]')),
        ('informatives',
         lxml.etree.XPath('cluster/region[@area="informatives"]')),
        ('teaser-mosaic', lxml.etree.XPath('cluster[@area="teaser-mosaic"]')),
    ])

    keys = editable_areas.keys
    __contains__ = editable_areas.__contains__

    _type_xml = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'type', zeit.content.cp.interfaces.ICenterPage['type'])
    _type_dav = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ICenterPage['type'],
        zeit.content.cp.interfaces.DAV_NAMESPACE, 'type')

    header_image = zeit.cms.content.property.SingleResource(
        '.head.header_image',
        xml_reference_name='image', attributes=('base-id', 'src'))

    snapshot = zeit.cms.content.property.SingleResource(
        '.head.snapshot',
        xml_reference_name='image', attributes=('base-id', 'src'))

    topiclink_title = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink_title',
        zeit.content.cp.interfaces.ICenterPage['topiclink_title'])

    topiclink_label_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_1',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_1'])

    topiclink_url_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_1',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_1'])

    topiclink_label_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_2',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_2'])

    topiclink_url_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_2',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_2'])

    topiclink_label_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_3',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_3'])

    topiclink_url_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_3',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_3'])

    og_title = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_title',
        zeit.content.cp.interfaces.ICenterPage['og_title'])

    og_description = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_description',
        zeit.content.cp.interfaces.ICenterPage['og_description'])

    og_image = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_image',
        zeit.content.cp.interfaces.ICenterPage['og_image'])

    def __getitem__(self, key):
        xml = self.editable_areas[key](self.xml['body'])[0]
        area = zope.component.getMultiAdapter(
            (self, xml),
            zeit.edit.interfaces.IArea,
            name=key)
        return zope.container.contained.contained(area, self, key)

    def updateMetadata(self, content):
        # Note that this method is a shortcut using XPath to query instead of
        # instantiating all blocks and their content objects to find the
        # matching one (since that's probably too expensive). So actually the
        # updating should be performed by the respective blocks (or their
        # ReferenceProperties) and not by duplicating their
        # implementation/serialzation details here.

        # Support renaming (see doc/implementation/move.txt).
        possible_ids = set((
            content.uniqueId,) + IRenameInfo(content).previous_uniqueIds)
        unique_ids = ' or '.join(['@href=%s' % xml.sax.saxutils.quoteattr(x)
                                  for x in possible_ids])
        # @uniqueId is for free teasers only, and those can't be renamed.
        query = '//block[@uniqueId={id} or {unique_ids}]'.format(
            id=xml.sax.saxutils.quoteattr(content.uniqueId),
            unique_ids=unique_ids)
        for entry in self.xml.xpath(query):
            if entry.get('uniqueId', content.uniqueId) not in possible_ids:
                # ``entry`` is a free teaser, but ``content`` is the referenced
                # object. Skip it, since the metadata of the free teaser itself
                # is what counts.
                continue

            # migration code
            node = entry.find('references')
            if node is not None:
                entry.remove(node)

            if not entry.get('uniqueId', '').startswith(TEASER_ID_NAMESPACE):
                entry.set('href', content.uniqueId)
                entry.set('uniqueId', content.uniqueId)
            updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
                content, None)
            if updater is not None:
                updater.update(entry)

            modified = zeit.cms.workflow.interfaces.IModified(content, None)
            if modified is not None:
                date = ''
                if modified.date_last_modified:
                    date = modified.date_last_modified.isoformat()
                entry.set('date-last-modified', date)

            publish_info = zeit.cms.workflow.interfaces.IPublishInfo(content,
                                                                     None)
            if publish_info is not None:
                date = ''
                if publish_info.date_first_released:
                    date = publish_info.date_first_released.isoformat()
                entry.set('date-first-released', date)
                date = ''
                if publish_info.date_last_published:
                    date = publish_info.date_last_published.isoformat()
                entry.set('date-last-published', date)

            lsc = zeit.cms.content.interfaces.ISemanticChange(content, None)
            if lsc is not None:
                date = ''
                if lsc.last_semantic_change:
                    date = lsc.last_semantic_change.isoformat()
                entry.set('last-semantic-change', date)

    @property
    def type(self):
        return self._type_xml

    @type.setter
    def type(self, value):
        self._type_xml = value
        self._type_dav = value


class CenterPageType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = CenterPage
    interface = zeit.content.cp.interfaces.ICenterPage
    title = _('Centerpage 2009')
    type = 'centerpage-2009'


_test_helper_cp_changed = False


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(
        *[zeit.content.cp.interfaces.ICMSContentIterable(area)
          for area in context.values()])


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def cp_references(context):
    cms_content = list(zeit.content.cp.interfaces.ICMSContentIterable(context))
    images = [context.header_image, context.snapshot]
    images = [x for x in images if x]
    return cms_content + images


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_centerpage_on_checkin(context, event):
    for content in zeit.content.cp.interfaces.ICMSContentIterable(context):
        context.updateMetadata(content)

    context.header_image = context.header_image
    context.snapshot = context.snapshot


@zope.component.adapter(
    zope.interface.Interface,
    zope.lifecycleevent.IObjectModifiedEvent)
def modified_propagator(context, event):
    """Propagate a modified event to the center page for sublocation changes.
    """
    if zeit.content.cp.interfaces.ICenterPage.providedBy(context):
        return
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return
    zope.security.proxy.removeSecurityProxy(cp)._p_changed = True
    global _test_helper_cp_changed
    _test_helper_cp_changed = True


class Feed(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)
    zope.interface.implements(zeit.content.cp.interfaces.ICPFeed)

    items = zeit.cms.content.reference.MultiResource(
        '.feed.reference', 'related')

    def set_items_and_supress_errors(self, items):
        # XXX copy&paste from MultiResource.__set__, is there a better way to
        # do this?
        prop = type(self).items
        references = prop.references(self)
        value = tuple(
            references.create(x, suppress_errors=True) for x in items)
        super(zeit.cms.content.reference.MultiResource, prop).__set__(
            self, value)
        prop.update_metadata(self, suppress_errors=True)


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_feed_items(context, event):
    if not event.publishing:
        # This event should only happen while publishing. It used to be on
        # BeforePublish, but since that requires another checkin/checkout
        # cycle, and the centerpage is cycled during publish anyway, we can
        # register it like this and avoid the additional cycle.
        return
    feed = zeit.content.cp.interfaces.ICPFeed(context)
    feed.items = extract_feed_items(context)


def extract_feed_items(context):
    feed = zeit.content.cp.interfaces.ICPFeed(context)
    items = []
    check_items = []
    for item in feed.items:
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(item):
            check_item = item.original_content
        else:
            check_item = item
        items.append(item)
        check_items.append(check_item)

    teasers = zeit.content.cp.interfaces.ITeaseredContent(context)
    for item in teasers:
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(item):
            if item.original_content in check_items:
                continue
        elif item in check_items:
            continue
        items.insert(0, item)

    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.cp')
    max_items = max(len(teasers), int(config['cp-feed-max-items']))
    while len(items) > max_items:
        del items[-1]

    return items


def has_changed(context):
    context = zope.proxy.removeAllProxies(context)
    if context._p_jar is None:
        # If there no jar, no change will have been marked.
        return True
    return context._p_changed


class SiteControlTopicPages(grok.GlobalUtility):

    grok.implements(zeit.cms.sitecontrol.interfaces.ISitesProvider)
    grok.name('topicpage')

    def __iter__(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        type_index = SearchVar(
            'type', zeit.content.cp.interfaces.DAV_NAMESPACE)
        result = connector.search([type_index],
                                  type_index == 'topicpage')
        result = [zeit.cms.interfaces.ICMSContent(uid, None)
                  for uid, dummy in result]
        return (obj for obj in result if obj is not None)


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    # XXX This method duplicates the XML structure from cp-template.xml
    ElementMaker = lxml.objectify.ElementMaker(nsmap=collections.OrderedDict((
        ('cp', 'http://namespaces.zeit.de/CMS/cp'),
        ('py', 'http://codespeak.net/lxml/objectify/pytype'),
        ('xi', 'http://www.w3.org/2001/XInclude'),
        ('xsd', 'http://www.w3.org/2001/XMLSchema'),
        ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
    )))
    root = getattr(ElementMaker, context.xml.tag)(**context.xml.attrib)
    root.append(copy.copy(context.xml.head))
    root.append(lxml.objectify.E.body(
        lxml.objectify.E.cluster(
            zeit.content.cp.interfaces.IRenderedXML(context['lead']),
            zeit.content.cp.interfaces.IRenderedXML(context['informatives']),
            area='feature'),
        zeit.content.cp.interfaces.IRenderedXML(context['teaser-mosaic']),
    ))
    root.append(ElementMaker.feed())
    # We need to insert the feed items into the copied XML tree, so this
    # operation stays read-only regarding the context CP.
    feed = zeit.content.cp.interfaces.ICPFeed(CopyXMLHelper(root))
    feed.set_items_and_supress_errors(extract_feed_items(context))

    return root


class CopyXMLHelper(object):
    """Mechanical helper to make ICPFeed and its MultiResource work"""

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage)

    def __init__(self, xml):
        self.xml = xml
        self.uniqueId = None
        self.__parent__ = None


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def mark_cp_on_checkout(context, event):
    if (zeit.content.cp.interfaces.ICP2009.providedBy(context)
        or zeit.content.cp.interfaces.ICP2015.providedBy(context)):
        return
    zope.interface.alsoProvides(context, zeit.content.cp.interfaces.ICP2009)
