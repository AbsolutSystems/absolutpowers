"""Static contracts for native, copy-pasteable next-step handoffs."""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_repo_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class NativeCommandHandoffContractTest(unittest.TestCase):
    def test_shared_contract_has_native_forms_and_rejects_legacy_forms(self) -> None:
        contract = read_repo_text("references/harness-command-contract.md")
        self.assertIn("/absolutpowers:skill-name [args]", contract)
        self.assertIn("$absolutpowers skill-name [args]", contract)
        self.assertIn("one standalone, copy-pasteable command line", contract)
        self.assertIn("@implement @path", contract)

    def test_session_and_project_context_inject_the_handoff_rule(self) -> None:
        for path in ("CLAUDE.md", "hooks/session-context.md"):
            with self.subTest(path=path):
                text = read_repo_text(path)
                self.assertIn("standalone", text)
                self.assertIn("harness-command-contract.md", text)
                self.assertRegex(text, re.compile(r"copy-paste", re.IGNORECASE))

    def test_implement_epic_handoff_cannot_fall_back_to_bare_codex_form(self) -> None:
        prompt = read_repo_text("skills/implement/SKILL.md")
        self.assertIn("harness-command-contract.md", prompt)
        self.assertIn("copy-pasteable command line", prompt)
        self.assertIn("feature-discuss", prompt)
        self.assertNotIn("`feature-discuss` na `{epic-main-path}`", prompt)

    def test_canonical_handoff_skills_reference_the_shared_contract(self) -> None:
        paths = (
            "skills/analyze/SKILL.md",
            "skills/debug/SKILL.md",
            "skills/feature-discuss/SKILL.md",
            "skills/generate-tasks/SKILL.md",
            "skills/implement/SKILL.md",
            "skills/problem-discuss/SKILL.md",
            "skills/qa-review/SKILL.md",
            "skills/receiving-code-review/SKILL.md",
            "skills/review/SKILL.md",
            "skills/tech-debt/SKILL.md",
            "skills/triada-review/SKILL.md",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertIn("harness-command-contract.md", read_repo_text(path))

    def test_code_writing_sites_reference_the_doc_comment_style_file(self) -> None:
        paths = (
            "agents/implementation-worker.md",
            "skills/implement/SKILL.md",
            "skills/debug/SKILL.md",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertIn("doc-comment-style.md", read_repo_text(path))

    def test_active_policy_and_adr_do_not_promote_legacy_skill_prefixes(self) -> None:
        for path in (
            "references/fork-policy.md",
            "VENDORED.md",
            "docs/adr/2026-07-16-lightweight-task-routing.md",
        ):
            with self.subTest(path=path):
                text = read_repo_text(path)
                self.assertNotRegex(
                    text,
                    re.compile(r"`@(?:debug|ship|implement|review|triada-review)`"),
                )


if __name__ == "__main__":
    unittest.main()
