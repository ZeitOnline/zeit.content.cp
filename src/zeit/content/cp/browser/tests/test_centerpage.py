import mock
import zeit.cms.testing
import zeit.content.cp
import zope.testbrowser.testing


class PermissionsTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(PermissionsTest, self).setUp()
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.getLink('Checkin').click()

        self.producing = zope.testbrowser.testing.Browser()
        self.producing.addHeader('Authorization', 'Basic producer:producerpw')

    def test_normal_user_may_not_delete(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/island')
        self.assertNotIn('island/@@delete.html', b.contents)

    def test_producing_may_delete(self):
        b = self.producing
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/island')
        self.assertEllipsis('...<a...island/@@delete.html...', b.contents)

    def test_normal_user_may_not_retract_via_menu_item(self):
        b = self.browser
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open(
                'http://localhost/++skin++vivi/repository/online/2007/01/'
                'island')
            self.assertNotIn('island/@@retract', b.contents)

    def test_normal_user_may_not_retract_via_button(self):
        b = self.browser
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open(
                'http://localhost/++skin++vivi/repository/online/2007/01/'
                'island/workflow.html')
            with self.assertRaises(LookupError):
                b.getControl('Save state and retract now')

    def test_producing_may_retract_via_menu_item(self):
        b = self.producing
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open(
                'http://localhost/++skin++vivi/repository/online/2007/01/'
                'island')
            self.assertEllipsis('...<a...island/@@retract...', b.contents)

    def test_producing_may_retract_via_button(self):
        b = self.producing
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open(
                'http://localhost/++skin++vivi/repository/online/2007/01/'
                'island/workflow.html')
            with self.assertNothingRaised():
                b.getControl('Save state and retract now')