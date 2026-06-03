import pytest
from agentx_evolve.learning.outcome_models import (
    FlakyOutcomeDetector, FO_FLAKY, FO_STABLE, detect_flaky,
)


class TestFlakyOutcomeDetector:
    def test_stable_outcome_detection(self):
        detector = FlakyOutcomeDetector(threshold=0.7)
        for _ in range(10):
            detector.record_outcome(True)
        result = detect_flaky(detector)
        assert result == FO_STABLE

    def test_flaky_outcome_detection(self):
        detector = FlakyOutcomeDetector(threshold=0.7)
        for _ in range(5):
            detector.record_outcome(True)
        for _ in range(5):
            detector.record_outcome(False)
        result = detect_flaky(detector)
        assert result == FO_FLAKY

    def test_empty_history_returns_stable(self):
        detector = FlakyOutcomeDetector()
        assert detect_flaky(detector) == FO_STABLE

    def test_mixed_outcomes_just_above_threshold(self):
        detector = FlakyOutcomeDetector(threshold=0.7)
        for _ in range(7):
            detector.record_outcome(True)
        for _ in range(3):
            detector.record_outcome(False)
        result = detect_flaky(detector)
        assert result == FO_STABLE

    def test_mixed_outcomes_below_threshold(self):
        detector = FlakyOutcomeDetector(threshold=0.7)
        for _ in range(6):
            detector.record_outcome(True)
        for _ in range(4):
            detector.record_outcome(False)
        result = detect_flaky(detector)
        assert result == FO_FLAKY

    def test_custom_threshold(self):
        detector = FlakyOutcomeDetector(threshold=0.5)
        for _ in range(4):
            detector.record_outcome(True)
        for _ in range(6):
            detector.record_outcome(False)
        result = detect_flaky(detector)
        assert result == FO_FLAKY
