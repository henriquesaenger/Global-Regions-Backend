# Global Regions Backend

Plone add-on that stores reusable, named Volto block regions on the Plone Site.

## Data model

The add-on provides one optional JSON field, `global_regions`. Each key is a
region name selected by the integrating project, and its value is a
Volto-compatible block document:

```json
{
  "global_regions": {
    "site-navigation": {
      "blocks": {},
      "blocks_layout": { "items": [] }
    },
    "home-banner": {
      "blocks": {},
      "blocks_layout": { "items": [] }
    }
  }
}
```

The standard Plone REST API exposes the field through root `GET` and
`PATCH`. The backend validates the region shape and block layout; names,
placement, allowed block types, and presentation are frontend/project
concerns.
