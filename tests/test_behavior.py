from global_regions.behaviors import IGlobalBlockRegions
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import WrongContainedType

import pytest


def _region():
    return {
        "blocks": {
            "custom-block": {
                "@type": "project-specific-block",
                "allowedBlocks": ["another-project-block"],
            },
        },
        "blocks_layout": {"items": ["custom-block"]},
        "allowedBlocks": ["project-specific-block"],
    }


def test_global_regions_field_is_optional_and_unset_initially(portal):
    assert IGlobalBlockRegions.providedBy(portal)
    assert "global_regions" not in portal.__dict__
    assert getattr(portal, "global_regions", None) is None

    field = IGlobalBlockRegions["global_regions"]
    assert field.required is False
    assert field.default is None


def test_schema_accepts_arbitrary_region_names_and_block_types():
    value = {
        "site-navigation": _region(),
        "campaign-area": {
            "blocks": {
                "campaign": {
                    "@type": "campaign-block",
                },
            },
            "blocks_layout": {"items": ["campaign"]},
        },
    }

    IGlobalBlockRegions["global_regions"].validate(value)


def test_schema_requires_blocks_and_blocks_layout_for_each_region():
    field = IGlobalBlockRegions["global_regions"]

    with pytest.raises(WrongContainedType):
        field.validate({"site-navigation": {"blocks": {}}})

    with pytest.raises(WrongContainedType):
        field.validate({"site-navigation": {"blocks_layout": {"items": []}}})


def test_schema_rejects_layout_items_without_matching_blocks():
    field = IGlobalBlockRegions["global_regions"]

    with pytest.raises(ConstraintNotSatisfied):
        field.validate(
            {
                "campaign-area": {
                    "blocks": {},
                    "blocks_layout": {"items": ["missing"]},
                },
            }
        )
