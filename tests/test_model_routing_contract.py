"""Static contracts for model-routing.md being the single owner of model/effort tiers."""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_repo_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class ModelRoutingSingleOwnerContractTest(unittest.TestCase):
    def test_dispatch_sites_point_to_model_routing(self) -> None:
        paths = (
            "skills/implement/references/orchestrated-process.md",
            "skills/implement/SKILL.md",
            "skills/generate-tasks/SKILL.md",
            "skills/feature-discuss/SKILL.md",
            "skills/triada-review/SKILL.md",
            "skills/qa-review/SKILL.md",
            "skills/tech-debt/SKILL.md",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertIn("references/model-routing.md", read_repo_text(path))

    def test_step_o2_does_not_restate_the_tier_table(self) -> None:
        """Step O2 must point to model-routing.md, not keep a second copy of the tiers."""
        text = read_repo_text("skills/implement/references/orchestrated-process.md")
        self.assertNotIn("| Role | Tier | Model | When |", text)

    def test_harness_dispatch_and_model_routing_link_to_each_other(self) -> None:
        """harness-dispatch.md (how) and model-routing.md (what) must link, not overlap."""
        harness = read_repo_text("references/harness-dispatch.md")
        routing = read_repo_text("references/model-routing.md")
        self.assertIn("references/model-routing.md", harness)
        self.assertIn("references/harness-dispatch.md", routing)

    def test_named_gate_templates_carry_explicit_model_and_effort(self) -> None:
        """review-tasks / review-plan / review-implementation dispatches used to omit model
        entirely; every literal Agent(...) template for these gates must now carry both, not
        just some of them (each file may template the gate more than once: dispatch + re-review)."""
        checks = (
            ("skills/generate-tasks/SKILL.md", "review-tasks"),
            ("skills/feature-discuss/SKILL.md", "review-plan"),
            ("skills/implement/SKILL.md", "review-implementation"),
            ("skills/implement/references/orchestrated-process.md", "review-implementation"),
        )
        for path, role in checks:
            with self.subTest(path=path, role=role):
                text = read_repo_text(path)
                all_calls = re.findall(
                    rf'Agent\(subagent_type="{role}"[^)]*\)', text
                )
                tiered_calls = [
                    call
                    for call in all_calls
                    if 'model="opus"' in call and 'effort="xhigh"' in call
                ]
                self.assertTrue(all_calls, f"no Agent(subagent_type=\"{role}\") call found")
                self.assertEqual(
                    len(all_calls),
                    len(tiered_calls),
                    f"every {role} dispatch must carry model=\"opus\" effort=\"xhigh\"",
                )


if __name__ == "__main__":
    unittest.main()
