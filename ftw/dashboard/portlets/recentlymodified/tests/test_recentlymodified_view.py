from ftw.builder import Builder
from ftw.builder import create
from ftw.dashboard.portlets.recentlymodified.testing import FTW_RECENTLYMODIFIED_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.controlpanel.security import ISecuritySchema
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
import transaction
import unittest2 as unittest


class TestRecentlyModifiedView(unittest.TestCase):

    layer = FTW_RECENTLYMODIFIED_FUNCTIONAL_TESTING

    @browsing
    def test_only_friendly_types_are_displayed(self, browser):
        """
        This test makes sure that only friendly types are shown in the
        recently modified view.
        """
        portal = self.layer['portal']

        # Allow to create temp folders (not a friendly type) inside folders.
        portal_types = getToolByName(portal, 'portal_types')
        portal_types.get('Folder').allowed_content_types += ('TempFolder',)

        folder = create(Builder('folder').titled('My Folder'))
        create(Builder('document').titled('My Document').within(folder))

        # Create an unfriendly item which should not be in the results.
        create(Builder('temp folder').titled('Temp Folder').within(folder))

        browser.visit(portal, view='recently_modified_view')
        browser.css('form[name="searchresults"]')
        content = ', '.join(
            browser.css('form[name="searchresults"] dl dt').text
        )

        self.assertIn('My Folder', content)
        self.assertIn('My Document', content)

    @browsing
    def test_home_folder_contents_are_not_displayed(self, browser):
        portal = self.layer['portal']

        # Enable user folders.
        security_adapter = ISecuritySchema(portal)
        security_adapter.set_enable_user_folders(True)

        # Create a members folder.
        create(Builder('folder').with_id('Members'))

        # Login in the browser for the home folder to be created.
        browser.visit(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        transaction.commit()

        # There must be a home folder inside the members folder now.
        membership_tool = getToolByName(portal, 'portal_membership')
        members_folder = membership_tool.getMembersFolder()
        self.assertTrue(members_folder.hasObject('test_user_1_'),
                        msg='There is no members folder.')

        # Create content in the user's home folder. This content must not be
        # present in the results.
        home_folder = membership_tool.getHomeFolder()
        create(Builder('document').titled('My Document').within(home_folder))

        # Create more content which must be present in the portlet.
        folder = create(Builder('folder').titled('My Folder'))
        create(Builder('document').titled('Another Document').within(folder))

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

        # Create a members folder.
        create(Builder('folder').with_id('Members'))

        # Login in the browser for the home folder to be created.
        browser.visit(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        transaction.commit()

        # There must be a home folder inside the members folder now.
        membership_tool = getToolByName(portal, 'portal_membership')
        members_folder = membership_tool.getMembersFolder()
        self.assertTrue(members_folder.hasObject('test_user_1_'),
                        msg='There is no members folder.')

        # Create content in the user's home folder. This content must be
        # present in the results.
        home_folder = membership_tool.getHomeFolder()
        create(Builder('document').titled('My Document').within(home_folder))

        # Create more content which must be present in the portlet.
        folder = create(Builder('folder').titled('My Folder'))
        create(Builder('document').titled('Another Document').within(folder))

        browser.visit(portal, view='recently_modified_view')
        browser.css('form[name="searchresults"]')
        content = ', '.join(
            browser.css('form[name="searchresults"] dl dt').text
        )
        self.assertIn('Members', content)
        self.assertIn('My Document', content)
