from ftw.builder import Builder
from ftw.builder import create
from ftw.dashboard.portlets.recentlymodified.browser import recentlymodified
from ftw.dashboard.portlets.recentlymodified.testing import FTW_RECENTLYMODIFIED_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
import unittest as unittest


class TestPortlet(unittest.TestCase):
    """ Basic tests for the recentlymodifiedportlet
    """

    layer = FTW_RECENTLYMODIFIED_INTEGRATION_TESTING

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType, name='ftw.dashboard.portlets.recentlymodified')
        self.assertEquals(
            portlet.addview, 'ftw.dashboard.portlets.recentlymodified')

    def test_interfaces(self):
        portlet = recentlymodified.Assignment()
        self.failUnless(
            recentlymodified.IRecentlyModifiedPortlet.providedBy(portlet))

    def renderer(self, section=''):
        if not section:
            section = api.portal.get()
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
        folder = create(Builder('folder').titled(u'My Folder'))
        r = self.renderer(IUUID(folder))
        self.assertEqual(r.title, 'My Folder')

    def test_data(self):
        folder = create(Builder('folder'))

        r = self.renderer(IUUID(folder))
        self.assertEqual(r._data() > 0, True)

    def test_more_link(self):
        folder = create(Builder('folder'))

        r = self.renderer(IUUID(folder))
        url = r.more_link()
        portal = self.layer['portal']
        expected_url = '%s/recently_modified_view' % \
            portal.folder.absolute_url()
        self.assertEqual(url, expected_url)

    def test_add_portlet_with_addview(self):
        folder = create(Builder('folder'))

        column = getUtility(IPortletManager, name='plone.dashboard1')
        category = column.get(USER_CATEGORY)

        manager = category.get(TEST_USER_ID)

        self.assertIsNone(
            manager,
            "The user manager should not yet exists because the user "
            "have never logged in.")

        folder.restrictedTraverse(
            'ftw.dashboard.addRecentlyModified')()

        manager = category.get(TEST_USER_ID)
        self.assertEqual(
            'test_user_1_', manager.__name__,
            "Because the user manager have not existed, it have been "
            "created while adding the recentlymodified portlet")

        self.assertEqual(
            ['recentlyModified0'], manager._order,
            "The recentlymodified portlet should have been created")

        # We add another portlet
        folder.restrictedTraverse(
            'ftw.dashboard.addRecentlyModified')()

        self.assertEqual(
            ['recentlyModified0', 'recentlyModified1'], manager._order,
            "The second portlet should be appended to the manager.")

    def test_get_contettype_class_for(self):
        folder = create(Builder('folder'))
        create(Builder('document').within(folder))

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
        collection_data = {
            'container': api.portal.get(),
            'Title': 'Test Collection',
            'id': 'test_collection',
            'type': 'Collection',
        }
        collection = api.content.create(**collection_data)
        r = self.renderer(IUUID(collection))
        self.assertEqual(r._data() > 0, True)

    def test_caching_data_if_calling_public_data_method(self):
        folder = create(Builder('folder'))
        create(Builder('page').within(folder))

        portlet_renderer = self.renderer()

        self.assertEqual(len(portlet_renderer.recent_items()), 2)

        create(Builder('folder'))

        self.assertEqual(len(portlet_renderer.recent_items()), 2)
        self.assertEqual(len(portlet_renderer._data()), 3)

    def test_excludet_types_are_not_listed_in_portlet(self):
        folder = create(Builder('folder'))
        create(Builder('document').within(folder))
        create(Builder('document').within(folder))

        portlet_renderer = self.renderer()

        self.assertEqual(
            sorted([brain.portal_type for brain in portlet_renderer._data()]),
            sorted([u'Document', u'Document', u'Folder']))

        registry = getUtility(IRegistry)
        registry[
            'ftw.dashboard.portlets.recentlymodified.types_to_exclude'] = [
            u'Document']

        portlet_renderer = self.renderer()

        self.assertEqual(
            [brain.portal_type for brain in portlet_renderer._data()],
            [u'Folder'])
