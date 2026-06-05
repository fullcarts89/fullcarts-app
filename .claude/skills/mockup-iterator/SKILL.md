---
name: mockup-iterator
description: "Use when iterating on an existing static HTML mockup file. Patches specific sections in place via regex anchors instead of regenerating the whole file. Avoids the 300-line copy-paste cycle when only one section actually changed."
---

# Mockup Iterator

## When to use

You've built a static HTML mockup (typically self-contained: CSS + JS + embedded data + sections). The user is reviewing iteratively and asking for changes that touch one or two specific sections — not a full redesign.

Classic anti-pattern this prevents: rewriting the entire 800-line Python generator from scratch for every iteration, even when only the evidence-trail section changed.

## When NOT to use

- First-time mockup creation — write it from scratch the first time
- A change that touches the global CSS or layout primitives — do those edits in place
- Production code (Next.js components, real React) — those should be properly modular, not stringly-typed

## The pattern

Each major section of the mockup gets a **regex-stable anchor**. Then iteration is:

```python
import re

src = open('mockup.html').read()

# Build the new section
new_section = build_evidence_trail(data)  # returns the full <section>…</section> HTML

# Replace by anchor — match the section's <h2> heading as the unique fingerprint
src = re.sub(
    r'  <section class="block">\s*<div class="section-head"><h2>Evidence trail.*?</section>',
    new_section,
    src,
    count=1,
    flags=re.DOTALL,
)

open('mockup.html', 'w').write(src)
```

The key insight: a mockup's structure is stable; only its contents churn. Match the structure, replace the contents.

## Anchor naming convention

When you generate the first mockup, give each major section a unique `<h2>` (e.g. "Wall of Shame", "All Cadbury products", "Evidence trail", "15 years of shrinking"). Those headings become natural regex anchors for later targeted replacements.

Bad: `<h2>Stats</h2>` repeated three times — can't target individually.
Good: `<h2>Brand totals</h2>`, `<h2>Recent events</h2>`, `<h2>Coverage timeline</h2>` — each unique, each addressable.

## Numbers must derive from a single source

Even when patching individual sections, the rule from `~/.claude/CLAUDE.md` ("Mockup Data Consistency") still applies. If section A and section B both display the same count, only one of them gets the literal in HTML; the other gets a `<span class="js-NAME">` placeholder that a small JS block populates from the rendered DOM. Then both stay in sync regardless of which section the patch updated.

Pattern:

```html
<h1>Cadbury</h1>
<p>We've documented <strong><span class="js-product-count">76</span> products</strong>.</p>
…
<div class="stat-value"><span class="js-product-count">76</span></div>
```

```javascript
const n = document.querySelectorAll('.product-card').length;
document.querySelectorAll('.js-product-count').forEach(el => { el.textContent = n; });
```

## Cleanup obligations

After each patch, verify:

1. The anchor regex matched **exactly once** (`re.subn(...)` returning `(_, 1)`) — if it matched 0 or 2+ times, your anchor isn't unique enough
2. The patched section's data attributes still match what the JS expects (e.g. `data-name`, `data-events`, `data-worst` for sort/filter scripts)
3. Banners and snapshot dates get updated alongside data (e.g. the "DATA SNAPSHOT FROM YYYY-MM-DD" banner)
4. The mockup still opens cleanly in a browser — no broken closing tags from a misaligned regex

## Helper: skeleton generator function

```python
def regen_section(src: str, anchor_h2: str, new_html: str) -> str:
    """Replace a <section> by its <h2> heading. Anchor must match exactly once."""
    pattern = (
        r'  <section class="block">\s*<div class="section-head">'
        r'<h2>' + re.escape(anchor_h2) + r'.*?</section>'
    )
    new_src, n = re.subn(pattern, new_html, src, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"Anchor '{anchor_h2}' matched {n} times — expected 1")
    return new_src
```

Use this in every iteration script so misaligned anchors fail loudly.

## Workflow

1. Read the current mockup HTML
2. Pull fresh data (database query, JSON file, etc.)
3. Re-render only the section(s) that need updating
4. Replace via anchor regex
5. Write back to disk
6. Open in browser to verify

Five steps. ~50 lines of Python. Compared to regenerating the entire 800-line mockup script, that's an order of magnitude less code shuffling per iteration — and the diff is reviewable.
