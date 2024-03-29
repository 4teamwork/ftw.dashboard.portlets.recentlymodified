from ftw.builder import Builder
from ftw.builder import create
from ftw.dashboard.portlets.recentlymodified.testing import FTW_RECENTLYMODIFIED_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone import api
from plone.app.controlpanel.security import ISecuritySchema
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
import transaction
import unittest as unittest


class TestRecentlyModifiedView(unittest.TestCase):

    layer = FTW_RECENTLYMODIFIED_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestRecentlyModifiedView, self).setUp()
        folder_data = {
            'container': api.portal.get(),
            'type': 'Folder',
            'id': 'Members',
            'title': 'Members'
            }
        api.content.create(**folder_data)
        transaction.commit()

    @browsing
    def test_home_folder_contents_are_not_displayed(self, browser):
        portal = self.layer['portal']

        # Enable user folders.
        security_adapter = ISecuritySchema(portal)
        security_adapter.set_enable_user_folders(True)
        transaction.commit()

        # Login in the browser for the home folder to be created.
        browser.visit(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()

        # There must be a home folder inside the members folder now.
        membership_tool = getToolByName(portal, 'portal_membership')
        members_folder = membership_tool.getMembersFolder()
        self.assertIn('test_user_1_', members_folder, 'There is no members folder.')

        # Create content in the user's home folder. This content must not be
        # present in the results.
        home_folder = membership_tool.getHomeFolder()
        create(Builder('document').titled(u'My Document').within(home_folder))

        # Create more content which must be present in the portlet.
        folder = create(Builder('folder').titled(u'My Folder'))
        create(Builder('document').titled(u'Another Document').within(folder))

        browser.visit(portal, view='recently_modified_view')
        browser.css('form[name="searchresults"]')
        content = ', '.join(
            browser.css('form[name="searchresults"] dl dt').text
        )
        self.assertNotIn('Members', content)

    @browsing
    def test_home_folder_contents_are_displayed(self, browser):
        portal = self.layer['portal']

        registry = getUtility(IRegistry)
        registry['ftw.dashboard.portlets.recentlymodified.'
                 'exclude_members_folder'] = False

        # Enable user folders.
        security_adapter = ISecuritySchema(portal)
        security_adapter.set_enable_user_folders(True)
        transaction.commit()

        # Login in the browser for the home folder to be created.
        browser.visit(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()

        # There must be a home folder inside the members folder now.
        membership_tool = getToolByName(portal, 'portal_membership')
        members_folder = membership_tool.getMembersFolder()
        self.assertIn('test_user_1_', members_folder, 'There is no members folder.')

        # Create content in the user's home folder. This content must be
        # present in the results.
        home_folder = membership_tool.getHomeFolder()
        create(Builder('document').titled(u'My Document').within(home_folder))

        # Create more content which must be present in the portlet.
        folder = create(Builder('folder').titled(u'My Folder'))
        create(Builder('document').titled(u'Another Document').within(folder))

        browser.visit(portal, view='recently_modified_view')
        browser.css('form[name="searchresults"]')
        content = ', '.join(
            browser.css('form[name="searchresults"] dl dt').text
        )
        self.assertIn('Members', content)
        self.assertIn('My Document', content)
