---
name: wrap-up
description: "Use when user says 'wrap up', 'close session', 'end session', 'wrap things up', 'close out this task', or invokes /wrap-up. Runs end-of-session checklist for shipping, memory, and self-improvement."
---

# Session Wrap-Up

Run four phases in order. Each phase is conversational and inline — no separate documents. Present a consolidated report at the end.

## Phase 1: Ship It

**Commit review:**
1. Run `git status` in each repo directory that was touched during the session
2. If uncommitted changes exist, present a summary of what would be committed:
   - Files changed, added, or deleted
   - A proposed commit message following the project's conventional commits format
3. **Ask the user to confirm** before committing. If approved, commit and push
4. If no uncommitted changes, skip to step 5

**File placement check:**
5. If any files were created or saved during this session:
   - Verify they follow the project's naming convention
   - Verify they're in the correct subfolder per the project structure
   - If violations are found, **present the proposed renames/moves and ask for confirmation**
6. If any document-type files (.md, .docx, .pdf, .xlsx, .pptx) were created
   at the workspace root or in code directories, suggest moving them to the docs folder
   if they belong there — **ask before moving**

**Deploy:**
7. Check if the project has a deploy skill or script
8. If one exists, **ask the user if they want to deploy**
9. If none exists, skip — do not mention deployment

**Task cleanup:**
10. Check the task list for in-progress or stale items
11. Mark completed tasks as done, flag orphaned ones for user review

## Phase 2: Remember It

Review what was learned during the session. Decide where each piece of knowledge belongs in the memory hierarchy:

**Memory placement guide:**
- **Auto memory** (Claude writes for itself) — Debugging insights, patterns
  discovered during the session, project quirks
- **CLAUDE.md** (instructions for Claude) — Permanent project rules,
  conventions, commands, architecture decisions that should guide all future
  sessions
- **`.claude/rules/`** (modular project rules) — Topic-specific instructions
  that apply to certain file types or areas. Use `paths:` frontmatter to scope
  rules to relevant files (e.g., testing rules scoped to `tests/**`)
- **`CLAUDE.local.md`** (private per-project notes) — Personal WIP context,
  local URLs, sandbox credentials, current focus areas that shouldn't be
  committed
- **`@import` references** — When a CLAUDE.md would benefit from referencing
  another file rather than duplicating its content

**Decision framework:**
- Is it a permanent project convention? -> CLAUDE.md or `.claude/rules/`
- Is it scoped to specific file types? -> `.claude/rules/` with `paths:` frontmatter
- Is it a pattern or insight Claude discovered? -> Auto memory
- Is it personal/ephemeral context? -> `CLAUDE.local.md`
- Is it duplicating content from another file? -> Use `@import` instead

**Auto-save to auto memory** without asking — these are low-stakes and self-correcting. For all other memory locations (CLAUDE.md, rules, CLAUDE.local.md), **present the proposed additions and ask for approval**.

## Phase 3: Review & Apply

Analyze the conversation for self-improvement findings. If the session was short or routine with nothing notable, say "Nothing to improve" and proceed to Phase 4.

**Finding categories:**
- **Skill gap** — Things Claude struggled with, got wrong, or needed multiple
  attempts
- **Friction** — Repeated manual steps, things user had to ask for explicitly
  that should have been automatic
- **Knowledge** — Facts about projects, preferences, or setup that Claude
  didn't know but should have
- **Automation** — Repetitive patterns that could become skills, hooks, or
  scripts

**Action types:**
- **Auto memory** — Save an insight for future sessions (auto-apply)
- **CLAUDE.md** — Edit the relevant project or global CLAUDE.md (requires approval)
- **Rules** — Create or update a `.claude/rules/` file (requires approval)
- **Skill / Hook** — Document a new skill or hook spec for implementation (requires approval)
- **CLAUDE.local.md** — Create or update per-project local memory (requires approval)

Present a summary in two sections — proposed changes first, then no-action items:

```
Findings:

1. Skill gap: Cost estimates were wrong multiple times
   -> [CLAUDE.md] Propose: Add token counting reference table
   -> Awaiting approval

2. Knowledge: Worker crashes on 429/400 instead of retrying
   -> [Rules] Propose: Add error-handling rules for worker
   -> Awaiting approval

3. Automation: Checking service health after deploy is manual
   -> [Skill] Propose: Post-deploy health check skill spec
   -> Awaiting approval

4. Knowledge: Discovered pattern X during debugging
   -> [Auto memory] Saved automatically

---
No action needed:

5. Knowledge: Discovered X works this way
   Already documented in CLAUDE.md
```

**Wait for user approval** on all non-auto-memory items before applying.

## Phase 4: Publish It

After all other phases are complete, review the full conversation for material that could be published. Look for:

- Interesting technical solutions or debugging stories
- Community-relevant announcements or updates
- Educational content (how-tos, tips, lessons learned)
- Project milestones or feature launches

**If publishable material exists:**

Draft the article(s) for the appropriate platform and save to a drafts folder. Present suggestions with the draft:

```
All wrap-up steps complete. I also found potential content to publish:

1. "Title of Post" — 1-2 sentence description of the content angle.
   Platform: Reddit
   Draft saved to: Drafts/Title-Of-Post/Reddit.md
```

Wait for the user to respond. If they approve, post or prepare per platform. If they decline, the drafts remain for later.

**If no publishable material exists:**

Say "Nothing worth publishing from this session" and you're done.

**Scheduling considerations:**
- If the session produced multiple publishable items, do not post them all
  at once
- Space posts at least a few hours apart per platform
- If multiple posts are needed, post the most time-sensitive one now and
  present a schedule for the rest

## Safety Rules

- **Never auto-commit to main or push without user confirmation**
- **Never auto-deploy without user confirmation**
- **Never auto-rename or auto-move files without user confirmation**
- **Never write to CLAUDE.md or rules files without user confirmation**
- Auto memory is the only location that can be written without asking
- If a `--force` flag is explicitly passed by the user, skip confirmation gates
  for that invocation only
