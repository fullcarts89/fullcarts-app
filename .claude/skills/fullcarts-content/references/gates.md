# The Three Gates

Run all three on every script before it becomes a production packet. Any single failure
blocks the clip — fix it or drop it. Do not proceed on a 4/5. Canonical definitions live in
`docs/content/content-rules.md` and `docs/content/approved-claims.md`; this is the runnable form.

---

## Gate 1 — The 5 non-negotiables

```
[ ] DATA-DRIVEN   a specific, sourced number is on screen, traceable to a real artifact
[ ] INTERESTING   the first 3s open on a hook (face + bold claim), not b-roll or a dry stat
[ ] CREDIBLE      database framing present; day-job signature used only if this is a ~1-in-5
                  video; employer NOT named; humility where natural
[ ] RELATABLE     second person, kitchen-table language ("you", not "consumers")
[ ] REACTION      ends on a kicker + an explicit engagement ask (comment / share / tag)
```

## Gate 2 — Approved-claims (accuracy)

```
[ ] every stat traces to approved-claims.md §1 OR a fresh DB pull this batch
[ ] banner number is the live count, rounded DOWN ("2,200+"), never up
[ ] superlative is qualified: "largest FREE, PUBLIC, searchable" (never bare "largest")
[ ] NONE of the forbidden §3 claims:
      ✗ "3,000+"            ✗ "decades of data / since 1985"
      ✗ "cited by Consumer Reports / press"   ✗ employer named
      ✗ any number not traceable to the registry
[ ] day-job stays insinuated ("a company billions have used"), never the employer name
```

## Gate 3 — Three-bucket evidence

The one-question test for every visual: **"Could a viewer mistake this for evidence of a fact,
product, or number?"** Yes → it must be REAL. No → AI is fine, labeled.

```
[ ] BUCKET 1 (must be real): product on camera, kitchen-scale, real source charts
    (BLS/FRED/ICE screenshots), FullCarts page screen-records, real headlines, the
    creator's real face/voice on authority pieces
[ ] BUCKET 2 (AI allowed, labeled): intros/transitions/atmosphere/metaphor only;
    platform AI-content label toggled ON
[ ] BUCKET 3 (never): fabricated charts/graphs/maps/dashboards, recreated packaging/logos,
    an AI avatar of the creator reciting real data as if it were the real them
[ ] new/low-trust account → fully AI-free until it earns history
[ ] any data viz is either a REAL screenshot, or a Remotion overlay built from real DB
    numbers (video/ toolkit) — never an AI-generated chart
```

---

## If a gate fails
- **Gate 1 miss** → rewrite the weak beat (usually the hook or the CTA). Don't ship a flat clip.
- **Gate 2 miss** → pull the number fresh; if it can't be sourced, cut the claim.
- **Gate 3 miss** → swap the offending visual for a real screenshot + `SourceFrame`, or a
  Remotion overlay from real numbers. Never "fix" it by making the fake look more convincing.
