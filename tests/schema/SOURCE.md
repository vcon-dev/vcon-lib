# Source

`vcon_json_schema.json` is vendored (not generated) from the vCon working
group's reference schema, kept here so `tests/test_schema_compliance.py` can
validate library output offline and reproducibly.

- Repository: https://github.com/vcon-dev/vcon-adapter-template
- Path: `tests/schema/vcon_json_schema.json`
- Commit: `43c587121431b27b561002730e0fd5971d6c47ca`
- Commit date: 2026-09-25 16:59:22 -0400
- Fetched: 2026-09-26, via `raw.githubusercontent.com/vcon-dev/vcon-adapter-template/main/tests/schema/vcon_json_schema.json`

This matches the appendix schema in `draft-ietf-vcon-vcon-core-04` (the
schema's own `$id`/`description` say "unsigned form of vCon ... as defined
in RFCXXXX"). Re-vendor by re-running the fetch above and diffing against
this copy if the draft or the adapter-template's schema changes.
