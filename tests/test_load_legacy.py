"""Loading 0.4.0 input: what is migrated implicitly and what is kept as is."""

import json
import warnings

from vcon import Vcon
from tests.test_migration_0_4_0 import v04, rec, T0


class TestLoadPath:
    def signed(self, payload):
        import base64
        b = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).decode().rstrip("=")
        return {"payload": b(payload), "signatures": [{"protected": b({"alg": "RS256"}), "signature": "c2ln", "header": {"x5c": []}}]}

    def test_signed_040_is_not_migrated_on_load(self):
        s = self.signed(v04(dialog=[rec()]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            v = Vcon(s)
        assert v.migration_report is None
        assert v.vcon_dict["signatures"] == s["signatures"] and v.vcon_dict["payload"] == s["payload"]

    def test_signed_040_explicit_migration_still_works(self):
        v = Vcon.migrate_0_4_0_to_0_5_0(self.signed(v04(dialog=[rec()])))
        assert v.migration_report.resign_required and "signatures" not in v.vcon_dict

    def test_opt_out_keeps_legacy_fields_even_in_strict_property_mode(self):
        d = v04(redacted={"uuid": "x", "type": "PII"},
                dialog=[rec(originator=1, party_history=[{"party": 0, "time": T0, "event": "join"}])])
        v = Vcon(d, property_handling="strict", migrate_legacy=False)
        assert v.vcon_dict["redacted"] == {"uuid": "x", "type": "PII"}
        assert v.vcon_dict["dialog"][0]["party_history"] and v.vcon_dict["dialog"][0]["originator"] == 1
