from ftw.dashboard.portlets.recentlymodified.browser import recentlymodified
from ftw.dashboard.portlets.recentlymodified.testing \
    import FTW_RECENTLYMODIFIED_INTEGRATION_TESTING
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.utils import _getDottedName
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
from plone.app.testing import TEST_USER_ID
from plone.portlets.constants import USER_CATEGORY
import unittest2 as unittest


class TestPortlet(unittest.TestCase):
    """ Basic tests for the recentlymodifiedportlet
    """

    layer = FTW_RECENTLYMODIFIED_INTEGRATION_TESTING

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType, name='ftw.dashboard.portlets.recentlymodified')
        self.assertEquals(
            portlet.addview, 'ftw.dashboard.portlets.recentlymodified')

    def test_registered_interfaces(self):
        portlet = getUtility(
            IPortletType, name='ftw.dashboard.portlets.recentlymodified')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(
            ['zope.interface.Interface', ], registered_interfaces)

    def test_interfaces(self):
        portlet = recentlymodified.Assignment()
        self.failUnless(
            recentlymodified.IRecentlyModifiedPortlet.providedBy(portlet))

    def renderer(self, section=''):
        context = self.layer['portal']
        request = self.layer['request']
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.rightcolumn', context=context)
        assignment = recentlymodified.Assignment(section=section)

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        return renderer

    def test_portlet_renderer(self):
        self.failUnless(isinstance(
            self.renderer(), recentlymodified.Renderer))

    def test_title_no_section(self):
        """Title should return the portal title or the"""
        r = self.renderer()
        context_title = self.layer['portal'].Title()
        portlet_title = translate(r.title)

        self.assertEqual(context_title, portlet_title)

    def test_title_with_section(self):
        r = self.renderer('/folder1')
        self.assertEqual(r.title, 'Folder1')

    def test_data(self):
        r = self.renderer('/folder1')
        self.assertEqual(r.recent_items() > 0, True)

    def test_more_link(self):
        r = self.renderer('/folder1')
        url = r.more_link()
        portal = self.layer['portal']
        expected_url = '%s/recently_modified_view' % \
            portal.folder1.absolute_url()
        self.assertEqual(url, expected_url)

    def test_add_portlet_with_addview(self):
        portal = self.layer['portal']
        portal.folder1.restrictedTraverse(
            'ftw.dashboard.addRecentlyModified')()

        manager = getUtility(IPortletManager, name='plone.dashboard1')
        column = manager.get(USER_CATEGORY, {}).get(TEST_USER_ID, {})
        self.assertEqual(column.keys() > 1, True)

    def test_get_contettype_class_for(self):
        portal = self.layer['portal']
        brain = portal.portal_catalog({'portal_type': 'Document'})[0]
        self.assertEqual(
            self.renderer().get_contettype_class_for(brain),
            'contenttype-document')

    def test_assignment_title(self):
        portlet = recentlymodified.Assignment()
        self.assertEqual(
            portlet.title,
            'title_recentlyModifed_portlet')

    def test_section_is_topic(self):
        portal = self.layer['portal']
        portal.manage_addProduct['ATContentTypes'].addATTopic(
            id='test_topic',
            title='Test Topic')
        topic = portal.test_topic
        topic.reindexObject()
        topic.addCriterion('Type', 'ATPortalTypeCriterion')
        portal.REQUEST.set('crit__Type_ATPortalTypeCriterion_value',
                           ['Document'])
        topic.criterion_save()
        r = self.renderer('/test_topic')
        self.assertEqual(r.recent_items() > 0, True)
