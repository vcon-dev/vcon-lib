# Source

`vcon_json_schema.json` is vendored (not generated) from the vCon working
group's draft, kept here so `tests/test_schema_compliance.py` and
`tests/test_core05_examples.py` can validate library output offline and
reproducibly.

- Document: `draft-ietf-vcon-vcon-core-05`, Appendix C (JSON Schema, draft-07),
  syntax `0.5.0`. It is the unfolded `vcon_json_schema.json` of the draft's
  repository at tag `draft-ietf-vcon-vcon-core-05`; the draft prints the same
  bytes folded at 65 columns.
- The previous copy (core-04, `const` "0.4.0") was replaced; it remains in
  git history.

`examples/B1-...B9-*.json` are the Appendix B examples of the same draft,
unfolded from the repository's `.vcon` files. B6 is the signed (JWS) form and
B7 the encrypted (JWE) form; the schema describes the unsigned form only.

This schema is permissive: parameters and type values the draft does not define
do not fail validation. Re-vendor from the draft tag if the draft changes.
