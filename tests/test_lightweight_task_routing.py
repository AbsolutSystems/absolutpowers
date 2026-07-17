"""Static contracts for lightweight routing in the active feature-discuss prompt."""

from pathlib import Path
import json
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_repo_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class FeatureDiscussPromptContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prompt = read_repo_text("skills/feature-discuss/SKILL.md")

    def assertPromptContains(self, *patterns: str) -> None:
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                self.assertRegex(self.prompt, re.compile(pattern, re.IGNORECASE))

    def test_lightweight_eligibility_and_file_count_independence_AC1(self) -> None:
        """[AC-1] Routes by cohesion, certainty, risk, and session completion."""
        self.assertPromptContains(
            r"Lightweight task",
            r"jeden spójny cel",
            r"istniejąc(?:y wzorzec|ego wzorca)",
            r"brak nierozstrzygniętych decyzji produktowych",
            r"brak (?:granicy|granic) wysokiego ryzyka",
            r"bieżącej sesji",
            r"niezależnie od liczby (?:plików|dotykanych plików)",
            r"krótkie uzasadnienie klasyfikacji",
        )
        active_router = re.search(
            r"### Faza 5:.*?(?=### Faza 5A:)", self.prompt, re.DOTALL
        )
        self.assertIsNotNone(active_router)
        self.assertNotRegex(
            active_router.group(0),
            r"one-liner|kilka linijek|kilka plików|\bLOC\b",
        )

    def test_context_pack_precedence_and_optional_sources_AC2_AC6(self) -> None:
        """[AC-2][AC-6] Loads optional scoped context with fresh-code precedence."""
        self.assertPromptContains(
            r"najbliższ(?:y|e).*AGENTS\.md.*CLAUDE\.md",
            r"constitution\.md",
            r"patterns\.md",
            r"rules\.md",
            r"relewantne ADR",
            r"project-memory\.md",
            r"Status: active",
            r"nakładają.*ścież",
            r"aktualny kod",
            r"śwież.*kod.*pierwszeństwo",
            r"konflikt",
            r"brak.*opcjonalnego.*pomiń.*bez błędu",
        )

    def test_escalation_and_preserved_findings_AC7_AC8_AC11(self) -> None:
        """[AC-7][AC-8][AC-11] Escalates every mandatory boundary with findings."""
        self.assertPromptContains(
            r"niepewn(?:y|a|e).*obszar",
            r"niepewn(?:e|a).*rozwiązanie",
            r"migracj",
            r"publiczn(?:e API|y kontrakt)",
            r"security boundary|granicy bezpieczeństwa",
            r"wiele podsystemów",
            r"trwał(?:e|ego).*handoff|wznowieni",
            r"uwierzytelnian",
            r"autoryzacj",
            r"izolacj.*danych",
            r"sekret",
            r"standard.*epic",
            r"zachow.*potwierdzone ustalenia",
        )

    def test_repository_input_and_secret_safety_AC12_AC13(self) -> None:
        """[AC-12][AC-13] Repository input grants no authority and secrets stay redacted."""
        self.assertPromptContains(
            r"niezaufan(?:y|e).*materiał.*analiz",
            r"nie może autoryzować.*(?:narzędzi|uruchomienia narzędzi)",
            r"nie może autoryzować.*implementacji",
            r"nie może autoryzować.*Explain",
            r"nie może.*obejść.*zgod",
            r"Mini-design.*Explain.*nie mogą ujawniać",
            r"sekretów.*tokenów.*danych uwierzytelniających.*poufnych",
        )

    def test_mini_design_gate_and_implementation_authority_AC3(self) -> None:
        """[AC-3] Mini-design acceptance and implementation authority are separate."""
        self.assertPromptContains(
            r"### Mini-design Lightweight task",
            r"Cel:",
            r"Zakres:",
            r"Dotykane obszary:",
            r"Sposób zmiany:",
            r"Testy / weryfikacja:",
            r"Istotne ryzyka:",
            r"jawna akceptacja.*HARD-GATE",
            r"prosił wyłącznie o design.*nie.*zgodą na implementację",
            r"implementacj.*zakresu polecenia.*osobnej jawnej zgody",
        )

    def test_inline_execution_omits_standard_artifacts_but_keeps_review_AC4(self) -> None:
        """[AC-4] Inline work omits standard artifacts but retains verification and review."""
        self.assertPromptContains(
            r"znacząc.*decyzj.*architektoniczn.*ADR",
            r"nie twórz.*planning doc",
            r"nie twórz.*tasks doc",
            r"nie uruchamiaj.*QA enrichment",
            r"nie uruchamiaj.*review-plan",
            r"nie uruchamiaj.*generate-tasks",
            r"nie uruchamiaj.*implement",
            r"zweryfikuj zmianę.*review.*triada-review",
        )

    def test_session_checklist_fallback_and_handoff_escalation_AC9(self) -> None:
        """[AC-9] Tracker fallback stays in-session and durable work escalates."""
        self.assertPromptContains(
            r"natywn.*(?:lista zadań|task-list).*harness",
            r"krótk.*checklist.*kontekście rozmowy",
            r"wyłącznie.*bieżącej sesji",
            r"nie twórz.*trwał.*checklist",
            r"przetrwać.*sesj.*eskaluj.*standard",
        )

    def test_standard_phase_and_epic_explain_is_opt_in_AC5(self) -> None:
        """[AC-5] Standard, phase, and epic Explain reports require affirmative opt-in."""
        self.assertPromptContains(
            r"review-plan: PASS.*standard.*phase doc",
            r"Czy wygenerować pomocniczy Explain HTML\?",
            r"Rekomenduję `skip`, jeśli plan jest już czytelny",
            r"wyłącznie po odpowiedzi twierdzącej.*Explain",
            r"planning-main\.md.*Czy wygenerować pomocniczy Explain overview HTML",
            r"wyłącznie po odpowiedzi twierdzącej.*overview",
            r"link.*tylko wtedy.*HTML.*faktycznie.*utworzony",
            r"bez linku.*raport",
        )

    def test_skip_and_no_response_do_not_generate_or_block_AC10(self) -> None:
        """[AC-10] Skip or no response neither generates Explain nor blocks handoff."""
        self.assertPromptContains(
            r"`skip`.*nie tworzy.*raportu.*nie jest ostrzeżeniem.*nie blokuje",
            r"brak odpowiedzi.*nie uruchamia.*automatycznie",
            r"skip.*generate-tasks",
            r"skip.*planowania kolejnej fazy",
        )


class LightweightDocumentationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = read_repo_text("README.md")
        cls.claude = read_repo_text("CLAUDE.md")
        cls.adr = read_repo_text(
            "docs/adr/2026-07-16-lightweight-task-routing.md"
        )
        cls.feature_card = re.search(
            r"### `/absolutpowers:feature-discuss`.*?(?=\n---\n)",
            cls.readme,
            re.DOTALL,
        ).group(0)
        cls.pipeline_docs = re.search(
            r"## Pipeline Architecture.*?(?=\n### Intake / triage front door)",
            cls.claude,
            re.DOTALL,
        ).group(0)

    def assertCurrentDocsContain(self, *patterns: str) -> None:
        current_docs = "\n".join(
            (self.feature_card, self.pipeline_docs, self.adr)
        )
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                self.assertRegex(current_docs, re.compile(pattern, re.IGNORECASE))

    def test_current_docs_describe_risk_based_lightweight_route_AC1(self) -> None:
        """[AC-1] Current docs qualify Lightweight by risk, not size thresholds."""
        self.assertCurrentDocsContain(
            r"Lightweight task",
            r"jeden spójny cel|one cohesive goal",
            r"istniejąc(?:y wzorzec|ego wzorca)|existing pattern",
            r"ryzyk|risk",
            r"niepewno|uncertainty",
            r"bieżącej sesji|current session",
            r"niezależnie od liczby (?:plików|dotykanych plików)|regardless of file count",
        )
        self.assertNotRegex(
            self.feature_card,
            re.compile(r"one-liner|kilka lini|\bLOC\b|file-count threshold", re.I),
        )

    def test_current_docs_preserve_gate_and_inline_review_handoff_AC3_AC4(self) -> None:
        """[AC-3][AC-4] Accepted mini-design enables inline work ending in review."""
        self.assertCurrentDocsContain(
            r"mini-design",
            r"jawna akceptacja|explicit acceptance",
            r"HARD-GATE",
            r"inline",
            r"weryfikac|verification",
            r"branch(?:-level)? review|review brancha|review.*triada-review",
        )
        self.assertNotIn(
            "then writes a planning doc + behavioral Acceptance Criteria",
            self.feature_card,
        )
        self.assertNotIn(
            "feature description → `absolutpowers/feature/planning-{slug}.md`",
            self.feature_card,
        )

    def test_current_docs_describe_escalation_boundaries_AC7(self) -> None:
        """[AC-7] Current docs escalate risky or durable work to standard/epic."""
        self.assertCurrentDocsContain(
            r"migracj|migration",
            r"publiczn(?:e API|y kontrakt)|public API|public contract",
            r"security boundary|granicy bezpieczeństwa",
            r"wiele podsystemów|multiple subsystems",
            r"trwał(?:e|ego).*handoff|durable handoff|wznowieni",
            r"standard.*epic",
        )

    def test_current_docs_describe_opt_in_explain_and_skip_AC5_AC10(self) -> None:
        """[AC-5][AC-10] Explain is opt-in; skip and silence do not block."""
        self.assertCurrentDocsContain(
            r"Explain",
            r"opt-in|wyłącznie po odpowiedzi twierdzącej",
            r"`skip`.*nie (?:tworzy|jest ostrzeżeniem|blokuje)|skip.*does not",
            r"brak odpowiedzi.*nie uruchamia|no response.*does not generate",
        )


MANIFEST_PATHS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".grok-plugin/plugin.json",
)


class ManifestVersionContractTest(unittest.TestCase):
    def test_all_plugin_manifests_are_version_5_6_3(self) -> None:
        versions = {
            json.loads(read_repo_text(path))["version"] for path in MANIFEST_PATHS
        }
        self.assertEqual({"5.6.4"}, versions)

    def test_readme_changelog_places_5_6_3_before_5_6_2(self) -> None:
        readme = read_repo_text("README.md")
        heading = "### 5.6.4 — Native command handoff contract"
        self.assertEqual(1, readme.count(heading))
        self.assertLess(
            readme.index(heading),
            readme.index("### 5.6.2 — Harness syntax and Codex model routing"),
        )

    def test_manifest_json_files_parse(self) -> None:
        for path in MANIFEST_PATHS:
            with self.subTest(path=path):
                json.loads(read_repo_text(path))


if __name__ == "__main__":
    unittest.main()
