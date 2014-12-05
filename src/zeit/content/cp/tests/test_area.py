import StringIO
import zeit.content.cp.area
import zeit.content.cp.centerpage
import zeit.content.cp.testing


CENTERPAGE = """
<centerpage
  xmlns:cp="http://namespaces.zeit.de/CMS/cp"
  xmlns:py="http://codespeak.net/lxml/objectify/pytype"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <head/>
  <body>
    <cluster area="feature">
      <region area="lead"/>
      <region area="informatives"/>
    </cluster>
    <cluster area="teaser-mosaic">
      {content}
    </cluster>
  </body>
  <feed/>
</centerpage>
"""

TEASERBAR = """
<region cp:type="teaser-bar" module="dmr" area="teaser-row-full"
        cp:__name__="{uuid}" supertitle="asd" teaserText="qwe"
        background_color="ff"/>
"""


class TeaserBarBackwardCompatibilityTest(
        zeit.content.cp.testing.FunctionalTestCase):

    def test_can_read_old_xml_with_teaser_bar_and_creates_areas(self):
        cp = zeit.content.cp.centerpage.CenterPage(StringIO.StringIO(
            CENTERPAGE.format(content=TEASERBAR.format(uuid='FOO'))))
        self.assertIsInstance(
            cp['teaser-mosaic']['FOO'], zeit.content.cp.area.Area)

    def test_can_read_old_xml_and_recognizes_teaserbar_ids_correctly(self):
        cp = zeit.content.cp.centerpage.CenterPage(StringIO.StringIO(
            CENTERPAGE.format(content=(
                TEASERBAR.format(uuid='FOO')
                + TEASERBAR.format(uuid='BAR')))))
        self.assertEqual(['FOO', 'BAR'], cp['teaser-mosaic'].keys())
