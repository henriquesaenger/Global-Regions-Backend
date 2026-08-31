import json

from global_regions import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider


REGION_SCHEMA = {
    "type": "object",
    "required": ["blocks", "blocks_layout"],
    "properties": {
        "blocks": {
            "type": "object",
            "additionalProperties": {"type": "object"},
        },
        "blocks_layout": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
    },
}

GLOBAL_REGIONS_SCHEMA = json.dumps(
    {
        "type": "object",
        "additionalProperties": REGION_SCHEMA,
    }
)


def valid_region_layout(value):
    """Ensure every layout item points to a block in the same region."""
    if not isinstance(value, dict):
        return False

    blocks = value.get("blocks")
    layout = value.get("blocks_layout")
    if not isinstance(blocks, dict) or not isinstance(layout, dict):
        return False

    items = layout.get("items")
    return isinstance(items, list) and all(item in blocks for item in items)


def valid_global_regions(value):
    """Validate a mapping of arbitrary region names to Volto block regions."""
    if value is None:
        return True

    return isinstance(value, dict) and all(
        valid_region_layout(region) for region in value.values()
    )


@provider(IFormFieldProvider)
class IGlobalBlockRegions(model.Schema):
    """Named block regions shared by the whole Plone site."""

    model.fieldset(
        "global_regions",
        label=_("Global regions"),
        fields=["global_regions"],
    )

    global_regions = JSONField(
        title=_("Global regions"),
        description=_(
            "Named Volto block regions available to the whole site."
        ),
        schema=GLOBAL_REGIONS_SCHEMA,
        required=False,
        default=None,
        missing_value=None,
        constraint=valid_global_regions,
    )
