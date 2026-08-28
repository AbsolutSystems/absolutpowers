"""Static contracts for the Depends-on/Requires dependency-field rules.

Guards the fix for the two-places-disagree defect: `Depends on` (Phase
Overview) is the declared single source of truth for phase ordering,
`Context Contract -> Requires` is a readiness contract naming artifacts (not
phases), the prose-negation idiom for "no prerequisites" is banned in favor
of an exact `None.`, cross-document Requires items carry an explicit
`External:` marker, and `review-tasks` gates any Depends-on/Requires
disagreement. These are textual contracts, not behavioral simulations —
they only prove the rule text survives future edits to these two files.
"""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_repo_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace runs so assertions survive incidental rewrapping."""
    return re.sub(r"\s+", " ", text)


class DependencyFieldOwnershipContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task_formats = read_repo_text(
            "skills/generate-tasks/references/task-formats.md"
        )
        cls.task_formats_flat = normalize_whitespace(cls.task_formats)
        cls.review_tasks = read_repo_text("agents/review-tasks.md")
        cls.review_tasks_flat = normalize_whitespace(cls.review_tasks)

    def test_depends_on_is_declared_the_ordering_source_of_truth(self) -> None:
        self.assertIn(
            "`Depends on` in `## Phase Overview` is the single source of truth "
            "for phase ordering",
            self.task_formats_flat,
        )
        self.assertIn(
            "and must never be read for ordering", self.task_formats_flat
        )

    def test_requires_field_is_scoped_to_artifacts_not_phase_ordering(self) -> None:
        self.assertIn(
            "an artifact, never a phase number or \"Phase N provides...\" "
            "narration; ordering belongs to `Depends on`, not here",
            self.task_formats_flat,
        )

    def test_no_prerequisites_wording_rule_bans_the_prose_negation_idiom(self) -> None:
        self.assertIn("**No-prerequisites wording:**", self.task_formats)
        self.assertIn("must read exactly", self.task_formats_flat)
        self.assertIn("`None.`", self.task_formats_flat)
        self.assertIn(
            "None (independent of Phase 1)", self.task_formats_flat
        )

    def test_cross_document_requires_rule_defines_the_external_marker(self) -> None:
        self.assertIn("**Cross-document Requires:**", self.task_formats)
        self.assertIn("External:", self.task_formats)

    def test_review_tasks_gates_depends_on_requires_disagreement(self) -> None:
        self.assertIn(
            "must agree on which phases it needs", self.review_tasks_flat
        )
        self.assertIn("`[WARN]` ORDERING issue", self.review_tasks_flat)


if __name__ == "__main__":
    unittest.main()
