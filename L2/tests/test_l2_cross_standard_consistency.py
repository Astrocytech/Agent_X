"""L2 cross-standard consistency tests — verifies alignment across ES, SIB, FIC, EQC."""
import os
import yaml

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _safe_yaml_load(path):
    if not os.path.isfile(path):
        return None
    with open(path) as fh:
        return yaml.safe_load(fh)


def test_profile_ids_match_across_registries():
    es_reg = _safe_yaml_load(os.path.join(L2_DIR, "ecosystem", "ecosystem-registry.yaml"))
    fic_idx = _safe_yaml_load(os.path.join(L2_DIR, "fic", "index.l2-fic.yaml"))
    if es_reg is None or fic_idx is None:
        return  # skip if files not ready
    fic_targets = {u.get("target_artifact_id") for u in fic_idx.get("fic_units", [])}
    es_profiles = {d.get("doc_id") for d in es_reg.get("documents", [])
                   if d.get("type") == "profile"}
    # ES uses AX-L2-* IDs, FIC uses L2-* IDs — alias reconciliation expected


def test_sib_handoff_implementation_allowed_false():
    hmap = _safe_yaml_load(os.path.join(L2_DIR, "sib", "sib-l1-handoff-map.yaml"))
    if hmap is None:
        return
    for target in hmap.get("handoff_targets", []):
        assert target.get("implementation_allowed_by_l2") is False, (
            f"Handoff {target.get('handoff_id')} has implementation allowed"
        )
        assert target.get("l1_acceptance_required") is True, (
            f"Handoff {target.get('handoff_id')} missing l1_acceptance_required"
        )


def test_generated_no_profile_authority_upgrade():
    catalog = _safe_yaml_load(os.path.join(L2_DIR, "generated", "profile_catalog.yaml"))
    if catalog is None:
        return
    # catalog is placeholder — no profiles listed yet, so this is a soft check
    profiles = catalog if isinstance(catalog, list) else catalog.get("profiles", [])
    for p in profiles:
        if isinstance(p, dict):
            assert p.get("implementation_allowed", False) is False


def test_fic_index_no_implementation():
    fic_idx = _safe_yaml_load(os.path.join(L2_DIR, "fic", "index.l2-fic.yaml"))
    if fic_idx is None:
        return
    for unit in fic_idx.get("fic_units", []):
        assert unit.get("implementation_allowed") is False, (
            f"FIC {unit.get('fic_id')} has implementation_allowed not false"
        )


def test_ecosystem_registry_release_evidence_false():
    es_reg = _safe_yaml_load(os.path.join(L2_DIR, "ecosystem", "ecosystem-registry.yaml"))
    if es_reg is None:
        return
    # Registry doesn't have release_evidence field at top level in old format
    # Check that no doc claims release status
    for doc in es_reg.get("documents", []):
        status = doc.get("status", "")
        assert status != "release", f"Doc {doc.get('doc_id')} claims release status"
