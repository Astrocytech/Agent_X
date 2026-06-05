import pytest
from agentx_evolve.prompt_contract.prompt_contract import (
    PromptContract, PromptVersionRecord, PromptContractRegistry,
    PC_SCHEMA_VERSION, PC_ACTIVE, PC_DEPRECATED, PC_RETIRED,
    ALL_PROMPT_CONTRACT_STATUSES,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_pc_schema_version():
    assert PC_SCHEMA_VERSION == "1.0"

def test_all_prompt_contract_statuses():
    assert PC_ACTIVE in ALL_PROMPT_CONTRACT_STATUSES
    assert PC_DEPRECATED in ALL_PROMPT_CONTRACT_STATUSES
    assert PC_RETIRED in ALL_PROMPT_CONTRACT_STATUSES
    assert len(ALL_PROMPT_CONTRACT_STATUSES) == 3

# ---------------------------------------------------------------------------
# PromptContract defaults
# ---------------------------------------------------------------------------

def test_prompt_contract_defaults():
    c = PromptContract()
    assert c.schema_version == "1.0"
    assert c.prompt_id == ""
    assert c.prompt_version == "1.0.0"
    assert c.status == PC_ACTIVE
    assert c.task_type == ""
    assert c.input_schema == ""
    assert c.output_schema == ""
    assert c.allowed_tools == []
    assert c.forbidden_behavior == []
    assert c.model_profiles == []
    assert c.template == ""
    assert c.test_cases == []
    assert c.created_at == ""
    assert c.updated_at == ""

def test_prompt_contract_custom():
    c = PromptContract(prompt_id="pc_001", task_type="IMPLEMENT_PATCH",
                       template="Do the thing", output_schema="patch.schema.json")
    assert c.prompt_id == "pc_001"
    assert c.task_type == "IMPLEMENT_PATCH"
    assert c.template == "Do the thing"
    assert c.output_schema == "patch.schema.json"

def test_prompt_contract_to_dict():
    c = PromptContract(prompt_id="pc_001", task_type="TEST")
    d = c.to_dict()
    assert d["prompt_id"] == "pc_001"
    assert d["task_type"] == "TEST"
    assert d["schema_version"] == "1.0"

# ---------------------------------------------------------------------------
# PromptVersionRecord defaults
# ---------------------------------------------------------------------------

def test_prompt_version_record_defaults():
    r = PromptVersionRecord()
    assert r.schema_version == "1.0"
    assert r.version_id == ""
    assert r.prompt_id == ""
    assert r.old_version == ""
    assert r.new_version == ""
    assert r.change_description == ""

def test_prompt_version_record_custom():
    r = PromptVersionRecord(prompt_id="pc_001", old_version="1.0.0", new_version="2.0.0",
                            change_description="Updated template")
    assert r.prompt_id == "pc_001"
    assert r.old_version == "1.0.0"
    assert r.new_version == "2.0.0"
    assert r.change_description == "Updated template"

def test_prompt_version_record_to_dict():
    r = PromptVersionRecord(version_id="pvr_001", prompt_id="pc_001")
    d = r.to_dict()
    assert d["version_id"] == "pvr_001"
    assert d["prompt_id"] == "pc_001"

# ---------------------------------------------------------------------------
# PromptContractRegistry
# ---------------------------------------------------------------------------

def test_registry_register():
    reg = PromptContractRegistry()
    c = PromptContract(prompt_id="pc_001", task_type="IMPLEMENT_PATCH", template="x", output_schema="y")
    reg.register(c)
    assert reg.get("pc_001") is c

def test_registry_get_nonexistent():
    reg = PromptContractRegistry()
    assert reg.get("nonexistent") is None

def test_registry_get_by_task():
    reg = PromptContractRegistry()
    c1 = PromptContract(prompt_id="pc_001", task_type="IMPLEMENT_PATCH", template="a", output_schema="s1")
    c2 = PromptContract(prompt_id="pc_002", task_type="IMPLEMENT_PATCH", template="b", output_schema="s2")
    c3 = PromptContract(prompt_id="pc_003", task_type="FIX_VALIDATION", template="c", output_schema="s3")
    reg.register(c1)
    reg.register(c2)
    reg.register(c3)
    results = reg.get_by_task("IMPLEMENT_PATCH")
    assert len(results) == 2
    assert c1 in results
    assert c2 in results

def test_registry_list_all():
    reg = PromptContractRegistry()
    assert reg.list_all() == []
    reg.register(PromptContract(prompt_id="pc_001", task_type="T1", template="t", output_schema="s"))
    reg.register(PromptContract(prompt_id="pc_002", task_type="T2", template="t", output_schema="s"))
    assert len(reg.list_all()) == 2

def test_registry_auto_assign_id():
    reg = PromptContractRegistry()
    c = PromptContract(task_type="TEST", template="t", output_schema="s")
    reg.register(c)
    assert c.prompt_id.startswith("pc-")
    assert c.created_at != ""
    assert c.updated_at != ""

def test_registry_remove():
    reg = PromptContractRegistry()
    c = PromptContract(prompt_id="pc_001", task_type="T", template="t", output_schema="s")
    reg.register(c)
    assert reg.remove("pc_001") is True
    assert reg.get("pc_001") is None
    assert reg.remove("nonexistent") is False

def test_registry_clear():
    reg = PromptContractRegistry()
    reg.register(PromptContract(prompt_id="pc_001", task_type="T", template="t", output_schema="s"))
    reg.clear()
    assert reg.list_all() == []

# ---------------------------------------------------------------------------
# PromptContractRegistry versioning
# ---------------------------------------------------------------------------

def test_registry_update_version():
    reg = PromptContractRegistry()
    c = PromptContract(prompt_id="pc_001", task_type="T", template="t", output_schema="s", prompt_version="1.0.0")
    reg.register(c)
    r = reg.update_version("pc_001", "2.0.0", change_description="Updated test cases")
    assert r is not None
    assert r.old_version == "1.0.0"
    assert r.new_version == "2.0.0"
    assert r.change_description == "Updated test cases"
    assert reg.get("pc_001").prompt_version == "2.0.0"

def test_registry_update_version_nonexistent():
    reg = PromptContractRegistry()
    r = reg.update_version("nonexistent", "2.0.0")
    assert r is None

def test_registry_get_version_history():
    reg = PromptContractRegistry()
    c = PromptContract(prompt_id="pc_001", task_type="T", template="t", output_schema="s")
    reg.register(c)
    reg.update_version("pc_001", "2.0.0")
    reg.update_version("pc_001", "3.0.0")
    history = reg.get_version_history("pc_001")
    assert len(history) == 2
    assert history[0].new_version == "2.0.0"
    assert history[1].new_version == "3.0.0"

def test_registry_get_version_history_empty():
    reg = PromptContractRegistry()
    assert reg.get_version_history("nonexistent") == []

# ---------------------------------------------------------------------------
# PromptContractRegistry status transitions
# ---------------------------------------------------------------------------

def test_registry_deprecate():
    reg = PromptContractRegistry()
    c = PromptContract(prompt_id="pc_001", task_type="T", template="t", output_schema="s")
    reg.register(c)
    assert reg.deprecate("pc_001") is True
    assert c.status == PC_DEPRECATED

def test_registry_deprecate_nonexistent():
    reg = PromptContractRegistry()
    assert reg.deprecate("nonexistent") is False

def test_registry_retire():
    reg = PromptContractRegistry()
    c = PromptContract(prompt_id="pc_001", task_type="T", template="t", output_schema="s")
    reg.register(c)
    assert reg.retire("pc_001") is True
    assert c.status == PC_RETIRED

def test_registry_retire_nonexistent():
    reg = PromptContractRegistry()
    assert reg.retire("nonexistent") is False

# ---------------------------------------------------------------------------
# PromptContractRegistry validation
# ---------------------------------------------------------------------------

def test_validate_contract_valid():
    c = PromptContract(prompt_id="pc_001", task_type="IMPLEMENT_PATCH",
                       template="Do the thing", output_schema="patch.schema.json")
    reg = PromptContractRegistry()
    errors = reg.validate_contract(c)
    assert errors == []

def test_validate_contract_missing_fields():
    c = PromptContract()
    reg = PromptContractRegistry()
    errors = reg.validate_contract(c)
    assert "prompt_id is required" in errors
    assert "task_type is required" in errors
    assert "template is required" in errors
    assert "output_schema is required" in errors

def test_validate_contract_invalid_status():
    c = PromptContract(prompt_id="pc_001", task_type="T", template="t",
                       output_schema="s", status="INVALID")
    reg = PromptContractRegistry()
    errors = reg.validate_contract(c)
    assert any("invalid status" in e for e in errors)
