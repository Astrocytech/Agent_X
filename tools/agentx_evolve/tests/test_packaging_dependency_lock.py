import pytest
from agentx_evolve.packaging.dependency_lock import DependencyLock


class TestDependencyLock:
    def test_defaults(self):
        lock = DependencyLock()
        assert lock.lock_id == ""
        assert lock.dependencies == []

    def test_add_dependency(self):
        lock = DependencyLock()
        lock.add_dependency("requests", "2.28.0", "abc123")
        assert len(lock.dependencies) == 1
        assert lock.dependencies[0]["name"] == "requests"

    def test_check_integrity_valid(self):
        lock = DependencyLock()
        lock.add_dependency("requests", "2.28.0", "abc123")
        result = lock.check_integrity()
        assert result["valid"] is True

    def test_check_integrity_missing_hash(self):
        lock = DependencyLock()
        lock.add_dependency("requests", "2.28.0", "")
        result = lock.check_integrity()
        assert result["valid"] is False
        assert "requests" in result["missing"]
