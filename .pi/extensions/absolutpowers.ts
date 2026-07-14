// Pi integration for the AbsolutPowers plugin.
//
// Mechanism adapted from obra/superpowers (MIT License, `.pi/extensions/superpowers.ts`)
// — see VENDORED.md. AbsolutPowers has no `using-superpowers` skill/dispatcher, so the
// re-injected content is read from `hooks/session-context.md` instead — the same file
// consumed by the Claude Code `hooks/session-start` hook (Phase 5). Do not duplicate that
// text inline here; both integrations must read the one shared source file.
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const EXTREMELY_IMPORTANT_MARKER = "<EXTREMELY_IMPORTANT>";
const BOOTSTRAP_MARKER = "absolutpowers session discipline bootstrap for pi";

const extensionDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(extensionDir, "../..");
const skillsDir = resolve(packageRoot, "skills");
const sessionContextPath = resolve(packageRoot, "hooks", "session-context.md");

let cachedBootstrap: string | null | undefined;

export default function absolutpowersPiExtension(pi: ExtensionAPI) {
	let injectBootstrap = true;

	pi.on("resources_discover", async () => ({
		skillPaths: [skillsDir],
	}));

	pi.on("session_start", async () => {
		injectBootstrap = true;
	});

	pi.on("session_compact", async () => {
		injectBootstrap = true;
	});

	pi.on("agent_end", async () => {
		injectBootstrap = false;
	});

	pi.on("context", async (event) => {
		if (!injectBootstrap) return;
		if (event.messages.some(messageContainsBootstrap)) return;

		const bootstrap = getBootstrapContent();
		if (!bootstrap) return;

		const bootstrapMessage = {
			role: "user" as const,
			content: [{ type: "text" as const, text: bootstrap }],
			timestamp: Date.now(),
		};

		const insertAt = firstNonCompactionSummaryIndex(event.messages);
		return {
			messages: [
				...event.messages.slice(0, insertAt),
				bootstrapMessage,
				...event.messages.slice(insertAt),
			],
		};
	});
}

function getBootstrapContent(): string | null {
	if (cachedBootstrap !== undefined) return cachedBootstrap;

	try {
		const sessionContext = readFileSync(sessionContextPath, "utf8").trim();
		cachedBootstrap = `${EXTREMELY_IMPORTANT_MARKER}
${BOOTSTRAP_MARKER}

The AbsolutPowers session discipline below is already loaded for this Pi session. Follow
it now.

${sessionContext}

${piToolMapping()}
</EXTREMELY_IMPORTANT>`;
		return cachedBootstrap;
	} catch {
		cachedBootstrap = null;
		return null;
	}
}

function piToolMapping(): string {
	return `## Pi tool mapping

Pi has native skills but does not expose Claude Code's \`Skill\` tool. When an
AbsolutPowers skill says to invoke a skill, load the relevant \`SKILL.md\` with \`read\`
when it applies, or let a human invoke \`/skill:name\` explicitly.

AbsolutPowers' pipeline skills also dispatch registered Claude Code agent types
(\`review-tasks\`, \`review-plan\`, \`review-implementation\`, \`phase-review\`,
\`qa-enrichment\`, \`implementation-worker\`) — those registrations do not exist on Pi. If a
subagent tool such as \`subagent\` from \`pi-subagents\` is available, use it, passing the
target \`agents/{name}.md\` content as the task prompt. Otherwise perform the review inline
in the current session and say plainly that it is not a fully isolated gate. See
\`references/pi-tools.md\` for the full mapping and degradation rules.

Pi does not ship a standard task-list tool. If an installed todo/task tool is available,
use it. Otherwise track work in the tasks/phase files already on disk, or a repo-local
\`TODO.md\`. Treat older \`TodoWrite\` references as this task-tracking action.`;
}

function messageContainsBootstrap(message: unknown): boolean {
	const content = (message as { content?: unknown }).content;
	if (typeof content === "string") return content.includes(BOOTSTRAP_MARKER);
	if (!Array.isArray(content)) return false;
	return content.some((part) => {
		return (
			part &&
			typeof part === "object" &&
			(part as { type?: unknown }).type === "text" &&
			typeof (part as { text?: unknown }).text === "string" &&
			(part as { text: string }).text.includes(BOOTSTRAP_MARKER)
		);
	});
}

function firstNonCompactionSummaryIndex(messages: unknown[]): number {
	let index = 0;
	while ((messages[index] as { role?: unknown } | undefined)?.role === "compactionSummary") {
		index += 1;
	}
	return index;
}
