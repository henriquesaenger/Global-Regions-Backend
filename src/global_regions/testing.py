from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import WSGI_SERVER_FIXTURE

import global_regions


class GlobalRegionsLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=global_regions)

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME,
            SITE_OWNER_PASSWORD,
            ["Manager"],
            [],
        )
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        applyProfile(portal, "global_regions:default")


FIXTURE = GlobalRegionsLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="GlobalRegionsLayer:IntegrationTesting",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="GlobalRegionsLayer:FunctionalTesting",
)
