# OPTIMADE 1.3 migration notes

This document tracks the qmpy 1.6 migration from OPTIMADE 1.0.0 to 1.3.0.
The runtime target remains Python 3.9 and Django 2.2.

## Mental model

The OPTIMADE implementation has four layers:

1. URL routing exposes versioned and unversioned endpoints.
2. Response views build JSON:API documents and pagination metadata.
3. The structure serializer maps OQMD records to OPTIMADE properties.
4. The Lark transformer converts OPTIMADE filters into Django `Q` objects.

An API-version update must keep all four layers consistent. Advertising a new
version in `/info` without updating filters, property definitions, and response
documents is not a specification upgrade.

## Implemented in the first v1.6 slice

- Advertise API version 1.3.0 from shared configuration.
- Serve the required `/v1` base and optional `/v1.3` and `/v1.3.0` bases.
- Return the unversioned `/versions` response as restricted CSV.
- Return status 553 for unsupported API versions.
- Build deployment-aware base URLs instead of embedding `oqmd.org`.
- Use the v1.3 response schema URL and RFC 3339 UTC timestamps.
- Return JSON:API-style error documents.
- Reject unrecognized, unprefixed query parameters.
- Support `api_hint`, JSON `response_format`, `response_fields`, offset
  pagination, and supported sort fields.
- Return 501 for the recognized but unsupported `dimension_slices` parameter.
- Use the official v1.2 filter grammar required by OPTIMADE 1.3, including
  boolean values and nested identifiers.
- Implement `IS KNOWN`/`IS UNKNOWN`, constant `type` filtering, and the required
  behavior for unknown foreign-provider properties.
- Reject legacy unprefixed OQMD filter aliases; OQMD extensions now require the
  `_oqmd_` prefix.
- Return string resource IDs, computed `elements_ratios`, consistent `species`,
  and standardized space-group properties.
- Describe standard properties with canonical OPTIMADE v1.2 definition IDs and
  describe OQMD-specific properties using the v1.2 property-definition format.

## Validation

The qmpy tests run under the `qmpy_3.9` Conda environment without a database:

```console
python qmpy/db/manage.py test qmpy.utils.oqmd_optimade
```

The current `optimade` validator package requires Python 3.10 or newer, so it
is intentionally installed and run in a separate environment. It is a test
tool, not a qmpy runtime dependency.

At the time of this migration, `optimade` 1.5.0 reports validator API version
1.2.0. It validates the new base-info and links documents. Its entry-info model
still expects the pre-property-definition v1.2 shape, so it cannot validate the
new v1.3 property-definition response directly.

## Work still required before claiming full compliance

- Validate database-backed structure list and detail responses against real or
  representative OQMD records.
- Run the full official validator against a local server connected to a test
  MySQL database.
- Complete mandatory query behavior for every advertised queryable property,
  especially timestamps and correlated `elements:elements_ratios` filters.
- Validate every custom property definition against the official v1.2 property
  meta-schema and add formal unit definitions where required.
- Decide whether to expose additional v1.3 structure properties and whether
  OQMD can provide a meaningful `last_modified` timestamp.
- Add CI validation once a deterministic database fixture is available.

The API must continue to advertise 1.0.0 in production until these changes are
reviewed and deployed together.
