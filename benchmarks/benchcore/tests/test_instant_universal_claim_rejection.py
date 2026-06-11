import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")


def load_claims():
    path = os.path.join(BENCHCORE, "instant_universal_claim_rejection_test.json")
    with open(path) as f:
        return json.load(f)


class TestInstantUniversalClaimRejection:

    def test_has_7_claims(self):
        claims = load_claims()
        assert len(claims) == 7

    def test_all_entries_have_required_fields(self):
        claims = load_claims()
        required = {"claim_id", "claim_text", "rejection_reason", "test_status"}
        for c in claims:
            missing = required - set(c.keys())
            assert not missing, f"{c['claim_id']} missing: {missing}"

    def test_all_claim_ids_have_correct_format(self):
        claims = load_claims()
        for c in claims:
            assert c["claim_id"].startswith("CLAIM-REJECT-")
            num = c["claim_id"].split("-")[-1]
            assert num.isdigit()

    def test_all_claim_texts_are_non_empty(self):
        claims = load_claims()
        for c in claims:
            assert c["claim_text"] and len(c["claim_text"]) > 5

    def test_all_rejection_reasons_are_non_empty(self):
        claims = load_claims()
        for c in claims:
            assert c["rejection_reason"] and len(c["rejection_reason"]) > 10

    def test_all_test_status_is_pass(self):
        claims = load_claims()
        for c in claims:
            assert c["test_status"] == "pass", f"{c['claim_id']} status is not pass"

    def test_no_duplicate_claim_ids(self):
        claims = load_claims()
        ids = [c["claim_id"] for c in claims]
        assert len(ids) == len(set(ids))

    def test_each_claim_is_meaningfully_distinct(self):
        claims = load_claims()
        texts = [c["claim_text"] for c in claims]
        assert len(texts) == len(set(texts))

    def test_rejection_reasons_are_not_identical(self):
        claims = load_claims()
        reasons = [c["rejection_reason"] for c in claims]
        assert len(reasons) == len(set(reasons))
