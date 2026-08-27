# Doc comment style: default shape, named escapes

**Read this file** before writing a doc comment (javadoc or equivalent) in code. Companion to
`references/code-reference-style.md`, which governs how you point at *code* by name; this file
governs what a doc comment *says* once you are writing one.

## Why

"Be concise" is not a rule anyone can check, so it either gets ignored or it cuts the one sentence
that actually carried information — under-documented public API is a worse outcome than one extra
line, and that trade must not be made. The fix is a default shape with a named list of escapes: the
checkable question becomes "which of these reasons requires the extra lines," not "is this concise."

## Rule 2 — a doc comment should not restate the signature

The signature already states the parameter names and the return type. A doc comment that only
repeats them in prose adds nothing and is one more thing that can go stale. Say what the signature
cannot express instead: invariants, units, ownership, failure modes, or why a surprising choice is
that way. This is not license to skip documenting — it redirects effort toward the part of a doc
comment that actually carries information.

## Rule 3 — default shape, named escapes

**Default:** one sentence, written for the caller — what they need to know to use it correctly.

**Escapes** — additional lines are warranted when, and only when, one of these applies:

- an invariant or precondition the signature cannot express;
- the unit or scale of a number (minor units, percent vs fraction, timezone, rounding mode);
- ownership or lifecycle — who closes it, who may mutate it, whether a returned collection is a copy;
- a failure mode — what it throws and under what condition;
- thread-safety or reentrancy;
- a surprising decision, with the reason — ideally citing the governing document or spec;
- a deprecation notice naming the replacement and the migration path;
- a cross-reference to another declaration that must be reviewed or changed alongside this one;
- an operational prerequisite the signature cannot express — a required index, a complexity or
  scaling characteristic, a resource limit — even when nothing throws if it is missing.

**The escape must be evident from the text.** A reviewer reads the escape off the extra lines
themselves, never infers unstated intent — point at which reason above the words serve. No label
is required (`Invariant:`, `Thread-safety:` are not mandatory), but if no reader can say which
reason the content serves, the escape does not apply and the lines are padding.

**Never document at all:**

- a getter or setter whose name already says what it does;
- a pure delegation whose target is obvious;
- a restatement of the class name in the class doc;
- a step-by-step description of the method body — this duplicates the code and goes stale with
  every edit to the method, and nothing warns you when it does.

**No hard line or word cap.** A cap gets gamed and gives the wrong signal on the rare doc comment
that genuinely needs several lines because more than one escape applies at once. The named reason
is the mechanism, not a count.

**Under-documenting is a failure too.** The one-sentence default is not license to drop an escape
that actually applies — when one of the conditions above holds, write the extra line; skipping it
is the failure mode this file is written against, just as much as padding is.
