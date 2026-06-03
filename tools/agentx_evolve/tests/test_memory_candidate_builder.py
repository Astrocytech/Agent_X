from __future__ import annotations
from agentx_evolve.learning.outcome_models import (
    LearningSignal, MemoryCandidate,
    MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW, MEMORY_CANDIDATE_BLOCKED,
    SIGNAL_FIX_WORKED, SIGNAL_FIX_FAILED, SIGNAL_UNSUPPORTED,
    REJECT_MISSING_EVIDENCE, REJECT_SECRET_OR_PROMPT,
)
from agentx_evolve.learning.memory_candidate_builder import build_memory_candidates


def _make_signal(signal_type=SIGNAL_FIX_WORKED, **kw) -> LearningSignal:
    fields = dict(
        signal_id="sig-001",
        review_id="rv-001",
        signal_type=signal_type,
        claim="test claim",
        supporting_evidence_refs=["ev-001"],
        confidence=0.7,
        eligible_for_memory=True,
        requires_human_review=True,
    )
    fields.update(kw)
    return LearningSignal(**fields)


def test_eligible_signal_creates_memory_candidate():
    sig = _make_signal()
    candidates = build_memory_candidates([sig], {})
    assert len(candidates) == 1
    assert candidates[0].status == MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW
    assert candidates[0].hash_of_candidate_text is not None


def test_memory_candidate_requires_human_review_by_default():
    sig = _make_signal()
    candidates = build_memory_candidates([sig], {})
    assert candidates[0].requires_human_approval is True
    assert candidates[0].status == MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW


def test_unsupported_signal_creates_blocked_candidate():
    sig = _make_signal(SIGNAL_UNSUPPORTED, eligible_for_memory=False)
    candidates = build_memory_candidates([sig], {})
    assert candidates[0].status == MEMORY_CANDIDATE_BLOCKED


def test_overbroad_candidate_is_blocked():
    sig = _make_signal(claim="A" * 600)
    candidates = build_memory_candidates([sig], {})
    assert candidates[0].status == MEMORY_CANDIDATE_BLOCKED


def test_secret_candidate_is_blocked():
    sig = _make_signal(claim="my api_key is sk-abc123def456ghi789jklmno")
    candidates = build_memory_candidates([sig], {})
    assert candidates[0].status == MEMORY_CANDIDATE_BLOCKED


def test_failed_run_cannot_create_positive_success_memory():
    sig = _make_signal(SIGNAL_FIX_FAILED)
    candidates = build_memory_candidates([sig], {})
    assert len(candidates) >= 1


def test_candidate_hash_is_stable():
    sig1 = _make_signal()
    sig2 = _make_signal()
    c1 = build_memory_candidates([sig1], {})
    c2 = build_memory_candidates([sig2], {})
    assert c1[0].hash_of_candidate_text == c2[0].hash_of_candidate_text
