from ftw.dashboard.portlets.recentlymodified.browser import recentlymodified
from ftw.dashboard.portlets.recentlymodified.testing \
    import FTW_RECENTLYMODIFIED_INTEGRATION_TESTING
from ftw.builder import Builder
from ftw.builder import create
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from plone.registry.interfaces import IRegistry
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
        create(Builder('folder').titled('My Folder'))
        r = self.renderer('/my-folder')
        self.assertEqual(r.title, 'My Folder')

    def test_data(self):
        create(Builder('folder'))

        r = self.renderer('/folder')
        self.assertEqual(r._data() > 0, True)

    def test_more_link(self):
        create(Builder('folder'))

        r = self.renderer('/folder')
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
