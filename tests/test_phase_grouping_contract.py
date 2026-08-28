"""Static contracts for the phase-grouping default and the planning-doc Scope section.

Guards two related fixes: `generate-tasks` no longer pushes phase sizing in one
direction only (split-only-for-a-named-reason default, plus the counter-pressure
that an over-split plan is also a defect and the "keep a large phase whole"
escape hatch), and `planning-formats.md`'s file-by-file Scope section now
carries per-file symbols instead of bare filenames. These are textual
contracts, not behavioral simulations — they only prove the rule text survives
future edits to these two files.
"""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_repo_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace runs so assertions survive incidental rewrapping.

    Also strips markdown blockquote `> ` line markers first, so a phrase that
    wraps across two `>`-prefixed lines reads as continuous prose instead of
    having a stray `>` spliced into the middle of it.
    """
    text = re.sub(r"(?m)^>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class PhaseGroupingDefaultContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generate_tasks = read_repo_text("skills/generate-tasks/SKILL.md")
        cls.generate_tasks_flat = normalize_whitespace(cls.generate_tasks)

    def test_default_is_coarsest_grouping_not_a_fixed_task_count(self) -> None:
        self.assertIn(
            "default to the coarsest grouping that still makes sense",
            self.generate_tasks_flat,
        )
        self.assertIn("split only where a named reason forces it", self.generate_tasks_flat)
        # The old one-directional heuristic must actually be gone, not just
        # supplemented -- otherwise the two guidances silently disagree.
        self.assertNotIn("Phase sizing by risk", self.generate_tasks)
        self.assertNotIn("group work into phases of 1-3 tightly related tasks", self.generate_tasks)

    def test_five_named_split_reasons_are_present(self) -> None:
        for reason in (
            "**Review surface**",
            "**Independence**",
            "**A database migration**",
            "**A change to a shared test base class or fixture**",
            "**A code-free audit whose output a later phase consumes**",
        ):
            with self.subTest(reason=reason):
                self.assertIn(reason, self.generate_tasks)

    def test_governing_idea_states_review_granularity_or_parallelism_tradeoff(self) -> None:
        self.assertIn(
            "a phase boundary buys either review granularity or parallelism, and only one",
            self.generate_tasks_flat,
        )
        self.assertIn(
            "if it buys neither, it should not exist", self.generate_tasks_flat
        )

    def test_too_small_is_named_as_a_defect(self) -> None:
        self.assertIn(
            "a phase too small is a plan defect just as a phase too large is",
            self.generate_tasks_flat,
        )

    def test_large_interacting_phase_may_stay_whole_with_multi_pass_review(self) -> None:
        self.assertIn(
            "**When a large phase must stay whole:**", self.generate_tasks
        )
        self.assertIn(
            "the same full diff reviewed repeatedly under different criteria",
            self.generate_tasks_flat,
        )
        self.assertIn(
            "a gate's issue budget is per review, not per line of diff",
            self.generate_tasks_flat,
        )


class PlanningScopeSymbolContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.planning_formats = read_repo_text(
            "skills/feature-discuss/references/planning-formats.md"
        )
        cls.planning_formats_flat = normalize_whitespace(cls.planning_formats)

    def test_scope_section_requires_symbols_not_just_filenames(self) -> None:
        self.assertIn(
            "Przy każdym pliku podaj zmieniane metody, konstruktory, pola lub regiony",
            self.planning_formats_flat,
        )

    def test_scope_section_references_code_reference_style_without_restating_it(self) -> None:
        # The Scope note must point at the owning file for the symbol/no-line-number
        # rule instead of duplicating its reasoning inline.
        scope_section = re.search(
            r"## Pliki do zmodyfikowania / utworzenia.*?(?=\n## )",
            self.planning_formats,
            re.DOTALL,
        )
        self.assertIsNotNone(scope_section)
        self.assertIn("references/code-reference-style.md", scope_section.group(0))
        self.assertNotIn(
            "goes stale the moment", scope_section.group(0)
        )  # code-reference-style.md's own reasoning, not duplicated here

    def test_scope_section_names_the_no_symbol_and_undecided_escapes(self) -> None:
        self.assertIn("nowy plik tworzony w całości", self.planning_formats_flat)
        self.assertIn("blok konfiguracji", self.planning_formats_flat)
        self.assertIn("adnotacja na poziomie klasy", self.planning_formats_flat)
        self.assertIn(
            "Gdy nie ustalono jeszcze, który symbol się zmieni", self.planning_formats_flat
        )

    def test_scope_section_states_the_prose_reconciliation_check(self) -> None:
        self.assertIn(
            "sprawdź, że każdy plik wymieniony w prozie", self.planning_formats_flat
        )


if __name__ == "__main__":
    unittest.main()
