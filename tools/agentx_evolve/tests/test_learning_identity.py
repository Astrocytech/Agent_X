import pytest
from agentx_evolve.learning.learning_identity import (
    LearningIdentity, register_learner, authenticate_learner,
)


class TestLearningIdentity:
    def test_register_learner(self):
        identity = register_learner("learner-1", "llm", version="2.0")
        assert identity.learner_id == "learner-1"
        assert identity.learner_type == "llm"
        assert identity.version == "2.0"
        assert identity.created_at != ""

    def test_register_and_authenticate(self):
        register_learner("learner-2", "tool", version="1.0")
        identity = authenticate_learner("learner-2")
        assert identity is not None
        assert identity.learner_id == "learner-2"

    def test_authenticate_wrong_type(self):
        register_learner("learner-3", "llm")
        identity = authenticate_learner("learner-3", expected_type="tool")
        assert identity is None

    def test_authenticate_nonexistent(self):
        identity = authenticate_learner("nonexistent")
        assert identity is None

    def test_register_with_metadata(self):
        register_learner("learner-4", "llm", metadata={"key": "val"})
        identity = authenticate_learner("learner-4")
        assert identity is not None
        assert identity.metadata == {"key": "val"}
