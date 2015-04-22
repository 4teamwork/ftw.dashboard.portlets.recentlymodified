from ftw.builder.session import BuilderSession
from ftw.builder.testing import BUILDER_LAYER, set_builder_session_factory
import ftw.dashboard.portlets.recentlymodified.tests.builders
from ftw.testing import FunctionalSplinterTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from zope.configuration import xmlconfig
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent


def functional_session_factory():
    sess = BuilderSession()
    sess.auto_commit = True
    return sess


class FtwRecentlymodifiedLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.dashboard.portlets.recentlymodified

        xmlconfig.file(
            'configure.zcml', ftw.dashboard.portlets.recentlymodified,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.dashboard.portlets.recentlymodified:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


class FunctionalBrowserlayerTesting(FunctionalSplinterTesting):
    """Support browserlayer"""

    def setUpEnvironment(self, portal):
        super(FunctionalBrowserlayerTesting, self).setUpEnvironment(portal)

        notify(BeforeTraverseEvent(portal, portal.REQUEST))


FTW_RECENTLYMODIFIED_FIXTURE = FtwRecentlymodifiedLayer()
FTW_RECENTLYMODIFIED_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_RECENTLYMODIFIED_FIXTURE, ),
    name="FtwRecentlymodified:Integration")
FTW_RECENTLYMODIFIED_FUNCTIONAL_TESTING = FunctionalBrowserlayerTesting(
    bases=(FTW_RECENTLYMODIFIED_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="FtwRecentlymodified:Functional")
