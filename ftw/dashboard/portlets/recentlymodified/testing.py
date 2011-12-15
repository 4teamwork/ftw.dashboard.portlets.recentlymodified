from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwRecentlymodifiedLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.dashboard.portlets.recentlymodified

        xmlconfig.file(
            'configure.zcml', ftw.dashboard.portlets.recentlymodified,
                context=configurationContext)

        # # installProduct() is *only* necessary for packages outside
        # # the Products.* namespace which are also declared as Zope 2
        # # products, using <five:registerPackage /> in ZCML.
        # z2.installProduct(app, 'ftw.book')
        # z2.installProduct(app, 'simplelayout.base')
        # z2.installProduct(app, 'simplelayout.types.common')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.dashboard.portal.recentlymodified:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


FTW_RECENTLYMODIFIED_FIXTURE = FtwRecentlymodifiedLayer()
FTW_RECENTLYMODIFIED_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_RECENTLYMODIFIED_FIXTURE,), name="FtwRecentlymodified:Integration")
