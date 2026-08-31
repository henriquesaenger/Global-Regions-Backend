from plone.dexterity.interfaces import IDexterityFTI
from global_regions import PACKAGE_NAME
from zope.component import getUtility


BEHAVIOR_NAME = "global_regions.global_block_regions"


def test_addon_is_installed(installer):
    assert installer.is_product_installed(PACKAGE_NAME)


def test_profile_version(profile_last_version):
    assert profile_last_version(f"{PACKAGE_NAME}:default") == "1000"


def test_behavior_is_applied_only_to_plone_site(portal):
    site_fti = portal.portal_types["Plone Site"]
    document_fti = getUtility(IDexterityFTI, name="Document")

    assert BEHAVIOR_NAME in site_fti.behaviors
    assert BEHAVIOR_NAME not in document_fti.behaviors


def test_uninstall_removes_behavior(installer):
    installer.uninstall_product(PACKAGE_NAME)

    site_fti = getUtility(IDexterityFTI, name="Plone Site")
    assert installer.is_product_installed(PACKAGE_NAME) is False
    assert BEHAVIOR_NAME not in site_fti.behaviors
