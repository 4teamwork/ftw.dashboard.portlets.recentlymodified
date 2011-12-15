from ftw.dashboard.portlets.recentlymodified.browser import recentlymodified
from ftw.dashboard.portlets.recentlymodified.testing \
    import FTW_RECENTLYMODIFIED_INTEGRATION_TESTING
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.utils import _getDottedName
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
import unittest2 as unittest


class TestPortlet(unittest.TestCase):
    """ Basic tests for the recentlymodifiedportlet
    """

    layer = FTW_RECENTLYMODIFIED_INTEGRATION_TESTING

    def testPortletTypeRegistered(self):
        portlet = getUtility(
            IPortletType, name='ftw.dashboard.portlets.recentlymodified')
        self.assertEquals(
            portlet.addview, 'ftw.dashboard.portlets.recentlymodified')

    def testRegisteredInterfaces(self):
        portlet = getUtility(
            IPortletType, name='ftw.dashboard.portlets.recentlymodified')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(
            ['zope.interface.Interface', ], registered_interfaces)

    def testInterfaces(self):
        portlet = recentlymodified.Assignment()
        self.failUnless(
            recentlymodified.IRecentlyModifiedPortlet.providedBy(portlet))

    def testRenderer(self):
        context = self.layer['portal']
        request = self.layer['request']
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.rightcolumn', context=context)
        assignment = recentlymodified.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)

        self.failUnless(isinstance(renderer, recentlymodified.Renderer))


class TestRenderer(unittest.TestCase):
    """ Tests for the renderer class of the recentlymodifiedportlet
    """

    layer = FTW_RECENTLYMODIFIED_INTEGRATION_TESTING

    def renderer(
        self,
        context=None,
        request=None,
        view=None,
        manager=None,
        assignment=None):

        context = context or self.layer['portal']
        request = request or self.layer['request']
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=context)
        assignment = assignment or recentlymodified.Assignment()

        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)

    def test_title(self):

        r = self.renderer()
        context_title = self.layer['portal'].Title()
        portlet_title = translate(r.title)

        self.assertEqual(context_title, portlet_title)
