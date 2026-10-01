"""Phase 1 verification tests for compute_score and engine resilience."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from engine.base import RuleResult, FraudRule
from engine.core import compute_score, to_verdict


# --- Stub rule classes for testing ---
class StubRule(FraudRule):
    def __init__(self, name, weight):
        self._name = name
        self._weight = weight

    @property
    def name(self): return self._name
    @property
    def weight(self): return self._weight

    async def evaluate(self, transaction, history):
        return RuleResult(self._name, 0.0, "stub", False)


def test_single_severe_rule_reaches_block():
    """One triggered rule at 100 with weight 0.3 among three rules => verdict BLOCK."""
    rules = [
        StubRule("velocity_check", 0.35),
        StubRule("amount_anomaly", 0.35),
        StubRule("geo_impossibility", 0.30),
    ]
    results = [
        RuleResult("velocity_check", 0.0, "ok", False),
        RuleResult("amount_anomaly", 0.0, "ok", False),
        RuleResult("geo_impossibility", 100.0, "Impossible speed", True),
    ]
    score = compute_score(results, rules)
    verdict = to_verdict(score)
    print(f"  score = {score}, verdict = {verdict}")
    # floor = 100 * 0.65 = 65, which is >= BLOCK threshold (60)
    assert score >= 60.0, f"Expected >= 60, got {score}"
    assert verdict == "BLOCK", f"Expected BLOCK, got {verdict}"


def test_critical_severity_forces_block():
    """A CRITICAL rule should force score to at least BLOCK threshold."""
    rules = [StubRule("critical_rule", 0.2)]
    results = [RuleResult("critical_rule", 30.0, "suspicious", True, severity="CRITICAL")]
    score = compute_score(results, rules)
    verdict = to_verdict(score)
    print(f"  score = {score}, verdict = {verdict}")
    assert score >= 60.0
    assert verdict == "BLOCK"


def test_no_triggered_rules_allow():
    """No triggered rules => low score => ALLOW."""
    rules = [StubRule("a", 0.5), StubRule("b", 0.5)]
    results = [
        RuleResult("a", 5.0, "low", False),
        RuleResult("b", 10.0, "low", False),
    ]
    score = compute_score(results, rules)
    verdict = to_verdict(score)
    print(f"  score = {score}, verdict = {verdict}")
    assert verdict == "ALLOW"


def test_rule_error_returns_safe_result():
    """A rule that raises should return a safe RuleResult via _safe_eval."""
    class BrokenRule(FraudRule):
        @property
        def name(self): return "broken"
        @property
        def weight(self): return 0.5
        async def evaluate(self, tx, hist):
            raise RuntimeError("kaboom")

    from engine.core import FraudEngine
    from engine.registry import RuleRegistry

    rule = BrokenRule()
    engine = FraudEngine.__new__(FraudEngine)
    engine.registry = RuleRegistry()
    engine.db = None  # not needed for _safe_eval

    result = asyncio.get_event_loop().run_until_complete(
        engine._safe_eval(rule, {}, [])
    )
    print(f"  result = {result}")
    assert result.triggered is False
    assert "Rule error" in result.reason
    assert result.score == 0.0


def test_score_clamped():
    """Score should be clamped to [0, 100]."""
    rules = [StubRule("x", 1.0)]
    results = [RuleResult("x", 150.0, "extreme", True)]
    score = compute_score(results, rules)
    print(f"  score = {score}")
    assert score <= 100.0


if __name__ == "__main__":
    tests = [
        test_single_severe_rule_reaches_block,
        test_critical_severity_forces_block,
        test_no_triggered_rules_allow,
        test_rule_error_returns_safe_result,
        test_score_clamped,
    ]
    passed = 0
    for t in tests:
        print(f"\n[RUN] {t.__name__}")
        try:
            t()
            print(f"  PASS")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
    print(f"\n{'='*40}")
    print(f"{passed}/{len(tests)} tests passed")
    if passed < len(tests):
        sys.exit(1)
