from copy import deepcopy

from global_regions.behaviors import IGlobalBlockRegions
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import RelativeSession
from zope.component import getMultiAdapter

import transaction


def _region(url=None):
    inner = {
        "@type": "project-specific-block",
        "allowedBlocks": ["another-project-block"],
    }
    if url is not None:
        inner["url"] = url

    return {
        "blocks": {
            "outer": {
                "@type": "container",
                "blocks": {"inner": inner},
            },
        },
        "blocks_layout": {"items": ["outer"]},
        "allowedBlocks": ["project-specific-block"],
    }


def test_global_regions_adapters_transform_nested_blocks(integration):
    portal = integration["portal"]
    request = integration["request"]
    target = api.content.create(
        container=portal,
        type="Document",
        id="link-target",
        title="Link target",
    )
    field = IGlobalBlockRegions["global_regions"]
    original = {"site-navigation": _region(target.absolute_url())}

    deserializer = getMultiAdapter(
        (field, portal, request),
        IFieldDeserializer,
    )
    stored = deserializer(deepcopy(original))
    stored_url = stored["site-navigation"]["blocks"]["outer"]["blocks"][
        "inner"
    ]["url"]
    assert "resolveuid/" in stored_url

    portal.global_regions = stored
    serializer = getMultiAdapter(
        (field, portal, request),
        IFieldSerializer,
    )
    serialized = serializer()

    assert serialized["site-navigation"]["blocks"]["outer"]["blocks"][
        "inner"
    ]["url"] == target.absolute_url()


def test_standard_root_get_patch_round_trip(functional):
    portal = functional["portal"]
    transaction.commit()
    session = RelativeSession(portal.absolute_url())
    session.headers.update({"Accept": "application/json"})
    session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    try:
        initial = session.get("")
        assert initial.status_code == 200
        assert initial.json()["global_regions"] is None

        regions = {
            "site-navigation": _region(),
            "campaign-area": {
                "blocks": {
                    "campaign": {
                        "@type": "unrestricted-region-block",
                    },
                },
                "blocks_layout": {"items": ["campaign"]},
            },
        }
        patched = session.patch("", json={"global_regions": regions})
        assert patched.status_code == 204

        fetched = session.get("")
        assert fetched.status_code == 200
        assert fetched.json()["global_regions"] == regions
    finally:
        session.close()


def test_partial_patch_can_return_updated_representation(functional):
    portal = functional["portal"]
    transaction.commit()
    session = RelativeSession(portal.absolute_url())
    session.headers.update(
        {
            "Accept": "application/json",
            "Prefer": "return=representation",
        }
    )
    session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    try:
        regions = {"campaign-area": _region()}
        patched = session.patch("", json={"global_regions": regions})

        assert patched.status_code == 200
        assert patched.json()["global_regions"] == regions
    finally:
        session.close()
