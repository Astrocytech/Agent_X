from agentx_evolve.contracts.contract_registry import MvpContractRegistry, MvpContract


class TestMvpContractRegistry:
    def test_register_and_resolve(self):
        r = MvpContractRegistry()
        c = MvpContract(contract_id="c1", contract_type="action", version="1.0.0")
        r.register(c)
        resolved = r.resolve("c1")
        assert resolved is not None
        assert resolved.contract_id == "c1"

    def test_unknown_contract_returns_none(self):
        r = MvpContractRegistry()
        assert r.resolve("nonexistent") is None

    def test_version_mismatch_fails(self):
        r = MvpContractRegistry()
        r.register(MvpContract(contract_id="c1", contract_type="action", version="1.0.0"))
        try:
            r.register(MvpContract(contract_id="c1", contract_type="action", version="2.0.0"))
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_validate_contract(self):
        r = MvpContractRegistry()
        c = MvpContract(contract_id="", contract_type="")
        issues = r.validate(c)
        assert len(issues) > 0

    def test_use_as_evidence(self):
        r = MvpContractRegistry()
        r.register(MvpContract(contract_id="c1", contract_type="action", version="1.0.0"))
        ev = r.use_as_evidence("c1")
        assert ev is not None
        assert ev["contract_id"] == "c1"
