"""Static contracts for test-scope-policy.md being the single owner of test-scope-and-timing rules."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]

POLICY = "references/test-scope-policy.md"

CLOSED_LIST_HEADINGS = (
    "## Requires the full unit suite — closed list",
    "## Requires a run against the real dependency — closed list",
)


def read_repo_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def closed_list_items(heading: str) -> tuple[str, ...]:
    """The bullet items written under one of the policy's 'closed list' headings.

    Read out of the policy itself rather than transcribed, so a newly added item is covered the
    moment it is written and no paraphrase can drift away from the text it guards.
    """
    policy = read_repo_text(POLICY)
    start = policy.find(heading)
    if start == -1:
        return ()
    section = policy[start + len(heading):]
    end = section.find("\n## ")
    if end != -1:
        section = section[:end]
    return tuple(
        line.strip()[2:].rstrip(";.")
        for line in section.splitlines()
        if line.strip().startswith("- ")
    )


VERIFICATION_SITES = (
    "agents/implementation-worker.md",
    "skills/generate-tasks/references/task-formats.md",
    "agents/phase-review.md",
    "agents/review-implementation.md",
    "agents/review-tasks.md",
    "skills/implement/SKILL.md",
    "skills/implement/references/orchestrated-process.md",
    "references/codex-tools.md",
    "references/grok-tools.md",
)


class TestScopePolicySingleOwnerContractTest(unittest.TestCase):
    def test_verification_sites_link_to_test_scope_policy(self) -> None:
        for path in VERIFICATION_SITES:
            with self.subTest(path=path):
                self.assertIn(POLICY, read_repo_text(path))

    def test_sites_do_not_restate_the_closed_lists(self) -> None:
        """No verifying site may carry the policy's closed-list items — single ownership means
        every site links to the policy instead of copying the cases it enumerates. Naming a list
        is a pointer; reproducing its items is a second copy that will drift."""
        for heading in CLOSED_LIST_HEADINGS:
            items = closed_list_items(heading)
            with self.subTest(heading=heading):
                self.assertTrue(
                    items,
                    f"no items parsed under {heading!r} — the policy's headings moved and this "
                    f"contract is no longer checking anything",
                )
            for path in VERIFICATION_SITES:
                text = read_repo_text(path)
                for item in items:
                    with self.subTest(path=path, item=item):
                        self.assertNotIn(item, text)

    def test_implementation_worker_timeout_ladder_gates_narrowing_on_breadth(self) -> None:
        """Narrowing is reserved for an incidental timeout; a phase on the full-unit-suite closed
        list must background the same broad target instead of narrowing it away."""
        text = read_repo_text("agents/implementation-worker.md")
        self.assertIn("If breadth is mandatory, narrowing is wrong", text)
        self.assertIn("Rerun the same broad target in the background", text)
        self.assertIn("the timeout is incidental", text)

    def test_orchestrator_timeout_exception_carries_the_breadth_gate(self) -> None:
        """Step O3's timeout exception must apply the worker's breadth gate rather than a plain
        narrow-and-retry, and must not re-order a backgrounded broad rerun the worker already
        spent — the ladder and the orchestrator have to agree on both halves."""
        text = read_repo_text("skills/implement/references/orchestrated-process.md")
        self.assertIn("apply the same breadth gate the worker", text)
        self.assertIn("when breadth **is** mandatory, the same broad target", text)
        self.assertIn("that attempt is spent", text)

    def test_final_verification_step_is_the_second_full_suite_run(self) -> None:
        """Step O5 must identify itself as the policy's second (not first, not extra) full-suite run."""
        text = read_repo_text("skills/implement/references/orchestrated-process.md")
        self.assertIn(
            "second of the policy's two required full-unit-suite runs", text
        )

    def test_phase_verification_template_site_points_to_change_kind_scope(self) -> None:
        """The phase-file template's Phase Verification field must point to the change-kind table
        and the run-twice rule, not restate them."""
        text = read_repo_text("skills/generate-tasks/references/task-formats.md")
        self.assertIn("Choosing the `## Phase Verification` command", text)
        self.assertIn("run-the-full-unit-suite-twice rule", text)


if __name__ == "__main__":
    unittest.main()
