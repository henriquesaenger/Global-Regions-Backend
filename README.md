# Global Regions Backend

Plone add-on that stores reusable, named Volto block regions on the Plone Site
root.

This package is the backend companion for a Volto global-regions integration.
It owns persistence, schema validation, and standard Plone REST API
serialization. The frontend add-on and the integrating theme own the editing
experience, available block types, region placement, and presentation.

It does **not** provide a custom REST endpoint. Global regions are stored in a
regular Dexterity JSON field on the site root and are read and written through
the standard Plone REST API with `GET` and `PATCH`.

## Features

- Dexterity behavior `global_regions.global_block_regions`, applied only to
  the **Plone Site** FTI
- One optional JSON field, `global_regions`
- Any number of named regions, each containing a Volto-compatible block layout
- Nested block values processed by `plone.restapi` block transformers
  (for example, internal-link `resolveuid` conversion)
- GenericSetup install and uninstall profiles
- Standard GET and PATCH access through the site root

## Compatibility

| Component | Version |
| --- | --- |
| Plone | 6.1 |
| Python | 3.12 |
| `plone.restapi` | 9.13.3+ |

## Installation

Add the package to your backend project dependencies:

```toml
dependencies = [
    "Products.CMFPlone>=6.1.1,<6.2",
    "plone.restapi>=9.13.3,<10",
    "plone-global-regions",
]
```

For a local checkout, declare it as an editable source. For example, with
`uv`:

```toml
[tool.uv.sources]
plone-global-regions = { path = "../Global Regions Backend", editable = true }
```

Rebuild the backend environment, restart the Plone instance, and install
**Global Regions: Install** from the Plone add-ons control panel.

The default GenericSetup profile:

- depends on `plone.restapi:default`
- adds `global_regions.global_block_regions` to the Plone Site FTI

Uninstalling removes the behavior from the FTI. Existing values already stored
on the site object are not deleted.

## Data model

After installation, the Plone Site provides `IGlobalBlockRegions`. Its
`global_regions` field is optional and initially unset (`null`).

The field is a mapping from a project-defined region name to a
Volto-compatible block document:

```json
{
  "global_regions": {
    "site-navigation": {
      "blocks": {
        "navigation": {
          "@type": "navigation"
        }
      },
      "blocks_layout": {
        "items": ["navigation"]
      }
    },
    "campaign-banner": {
      "blocks": {},
      "blocks_layout": {
        "items": []
      }
    }
  }
}
```

Region names are not prescribed by this package. A theme may, for example,
expose regions named `header` and `footer`; they are ordinary entries in the
same collection, not special backend fields.

Each region must contain:

```json
{
  "blocks": {},
  "blocks_layout": {
    "items": []
  }
}
```

The backend validates that:

- `global_regions` is an object when it has a value
- each region contains `blocks` and `blocks_layout`
- `blocks_layout.items` is an array of strings
- every item in `blocks_layout.items` exists as a key in `blocks`

The backend does **not** validate:

- nested block `@type` values
- allowed block types or maximum block counts
- region names or their page location
- rendering, styling, or theme-specific behavior

Those decisions belong to the frontend integration and theme. Extra keys on a
region object are stored as received.

## REST API

### Read

```http
GET /Plone HTTP/1.1
Accept: application/json
```

The site representation includes:

```json
{
  "global_regions": null
}
```

After regions are stored, the same key contains the full mapping. Nested block
serialization transformers run for every named region.

### Write

Send the complete collection for the field:

```http
PATCH /Plone HTTP/1.1
Accept: application/json
Content-Type: application/json
Prefer: return=representation
If-Match: "<etag>"
```

```json
{
  "global_regions": {
    "site-navigation": {
      "blocks": {
        "navigation": {
          "@type": "navigation"
        }
      },
      "blocks_layout": {
        "items": ["navigation"]
      }
    }
  }
}
```

By default, `PATCH` responds with `204 No Content`. Add
`Prefer: return=representation` when the updated site representation is
needed by the client.

On deserialization, nested blocks run through the standard REST API
transformers before storage. This keeps internal-link values consistent with
regular Volto block content.

> **Note**
>
> The REST API replaces the value of `global_regions` supplied in the request.
> A client that saves one named region should merge it with the current
> collection before sending the patch, so other named regions remain present.

## Responsibilities

| Layer | Responsibility |
| --- | --- |
| Global Regions Backend | Persistence, schema validation, and REST API block transformation |
| Volto integration | Fetching, merging, saving, and editing named regions |
| Theme or project | Region names, placement, allowed blocks, and rendering |

## Tests

```shell
uv sync --extra test
uv run pytest
```

The test suite covers GenericSetup installation, behavior assignment to the
Plone Site, validation constraints, REST API round-trips, and nested block
transformations.

## License

MIT. See [LICENSE](LICENSE).
