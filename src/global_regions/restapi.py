from copy import deepcopy

from global_regions.behaviors import IGlobalBlockRegions
from plone.base.interfaces import IPloneSiteRoot
from plone.restapi.blocks import iter_block_transform_handlers
from plone.restapi.blocks import visit_blocks
from plone.restapi.deserializer.blocks import BlocksJSONFieldDeserializer
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.blocks import BlocksJSONFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.schema import IJSONField
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


GLOBAL_REGIONS_FIELD_NAME = "global_regions"


def _is_global_regions_field(field):
    return (
        field.interface is IGlobalBlockRegions
        and field.getName() == GLOBAL_REGIONS_FIELD_NAME
    )


def _transform_blocks(context, blocks, transformer_interface):
    for block in visit_blocks(context, blocks):
        transformed = block.copy()
        for handler in iter_block_transform_handlers(
            context,
            block,
            transformer_interface,
        ):
            transformed = handler(transformed)
        block.clear()
        block.update(transformed)


def _transform_regions(context, regions, transformer_interface):
    for region in regions.values():
        _transform_blocks(
            context,
            region["blocks"],
            transformer_interface,
        )


@implementer(IFieldSerializer)
@adapter(IJSONField, IPloneSiteRoot, IBrowserRequest)
class GlobalRegionsJSONFieldSerializer(BlocksJSONFieldSerializer):
    """Serialize blocks nested in every named global region."""

    def __call__(self):
        if not _is_global_regions_field(self.field):
            return super().__call__()

        value = deepcopy(self.get_value())
        if value is None:
            return None

        _transform_regions(
            self.context,
            value,
            IBlockFieldSerializationTransformer,
        )
        return json_compatible(value)


@implementer(IFieldDeserializer)
@adapter(IJSONField, IPloneSiteRoot, IBrowserRequest)
class GlobalRegionsJSONFieldDeserializer(BlocksJSONFieldDeserializer):
    """Deserialize blocks nested in every named global region."""

    def __call__(self, value):
        if not _is_global_regions_field(self.field):
            return super().__call__(value)

        value = DefaultFieldDeserializer.__call__(self, value)
        if value is None:
            return None

        value = deepcopy(value)
        _transform_regions(
            self.context,
            value,
            IBlockFieldDeserializationTransformer,
        )
        return value
