# The Retention Spine

`hooks.md` wins the first 3 seconds. This file wins the **other 40**. It is the doctrine for the
*whole* script body — what happens after the hook lands, so the video actually retains instead of
front-loading a great hook onto a flat middle that bleeds viewers.

> **Why this exists:** the algorithm rewards **retention + interaction**, not hooks. A perfect
> 3-second hook on a boring body is still a low-performing video. The hook buys attention; the spine
> keeps it and converts it into the two signals distribution actually runs on: **watch-through** and
> **re-watch / interaction**.

Distilled from two creator masterclass reels (credited at the bottom) and reconciled with the
FullCarts house template (`cold-open → hook → lock-in → proof → trick → payoff → CTA`). It does not
replace that template — it sharpens two beats the template was thin on (**the re-hook** and **the
ending**) and adds one new lever (**the interaction loop**).

---

## The 6-beat retention spine (maps onto the house template)

| # | Spine beat | What it does | House-template beat | Already strong? |
|---|---|---|---|---|
| 1 | **Curiosity hook** | open the first loop (contrast) | hook (**The Snap**) | ✅ `hooks.md` |
| 2 | **Agitate the pain** | make them *lock in* — "this is about me" | **lock-in** (Emotional Lock-In) | ✅ our edge |
| 3 | **RE-HOOK** ⚠️ | re-grab attention at the sag (~30–45% mark) | *(NEW — insert before proof)* | ❌ **the gap** |
| 4 | **Establish context** | the facts, framed so the number lands | proof | ✅ |
| 5 | **Build to the solution** | the trick → the meaning/pattern | trick → payoff | ✅ |
| 6 | **Cut at peak → loop** ⚠️ | end at peak engagement, bait the re-watch | *(replaces a soft spoken CTA)* | ❌ **the gap** |

Beats 1, 2, 4, 5 are things FullCarts already does well — **agitation (beat 2) is our structural
advantage**, because shrinkflation is engineered to make victims blame themselves, so the
"it's not you" lock-in is unusually strong (see `hooks.md` → Emotional Lock-In). The two beats to
add deliberately to every script are **3 (re-hook)** and **6 (peak-cut loop)**.

---

## Beat 3 — the RE-HOOK (the biggest missing move)

Attention sags around the **30–45% mark** — right when the novelty of the hook wears off and before
the payoff arrives. A re-hook re-grabs them. Two mechanisms (use at least one, every video):

1. **Ask a new question** — open a *second* curiosity loop before closing the first.
   - *"But here's the part that should actually make you angry…"*
   - *"And it's not just this one product — guess which aisle is worst."*
2. **Switch the scene / cut hard** — a literal visual change resets attention. For FullCarts this is
   the **cut from the talking head INTO the `BeforeAfter` / `ShrinkReveal` overlay** — and it's free,
   because our format already alternates face ↔ evidence cutaway. Just *place the hardest cut at the
   sag*, on the line where you reveal the number, not earlier.

**FullCarts re-hook placement:** the cut into the receipt is your re-hook. Script the sharpest
visual reveal to land at ~12–15s of a 40s cut, on a re-hook line ("watch what happened to this exact
bag"). Pair with the camera track's `rehook` move (`FinalVideo` supports a fake-angle rehook — see
`docs/content/SESSION-HANDOFF.md`).

---

## Beat 6 — cut at PEAK, then loop (kill the soft outro)

End **on the sharpest stat or the cleanest "it's not you, it's them" line** — at peak engagement —
**not** on a soft spoken CTA ("follow for more", "link in bio"). A spoken CTA at the end *lowers*
the retention curve exactly where you want it highest, and kills the re-watch.

- **Spoken close = the peak-cut.** End on the number or the payoff, hard. *"…that bag is 38% emptier
  and nobody told you."* Cut.
- **The CTA lives in the CAPTION, not the VO.** `fullcarts.org`, the "look it up free" line, the
  hashtags — all caption. (Our captions already do this well; keep it. See `captions.md` patterns.)
- **Loop-bait:** end on a line that rewards an immediate re-watch — a detail the viewer only catches
  the second time, or a question that sends them back to the hook. The re-watch is a top distribution
  signal.

> **Reconciliation note:** the house template's final beat is "CTA". That still holds — but the CTA
> is a *caption/end-card* CTA, not a spoken one. The *spoken* script ends at beat 5's payoff, cut at
> peak. Don't talk past the payoff.

---

## The interaction loop (the distribution multiplier)

Retention gets you watch-through; **interaction loops get you re-watches and comments**, which is how
the biggest videos compound. The mechanic: design a moment that makes the viewer *do something* that
generates another view or a comment.

**Replay / pause loops** — engineer a reason to pause or re-watch:
- **"Pause on the receipt."** Put a real, dense source screenshot (`SourceFrame`) on screen for a beat
  too short to fully read — viewers pause and scrub. Each scrub is watch-time.
- **"Did you catch it?"** Hide a second detail in the `BeforeAfter` (the net-weight line, the
  "now with 20% more air") that rewards a second watch — then name it in the caption, not the VO.
- **Count-up reveals** (`StatCard` / `BudgetShareBars`) that resolve a beat after the VO moves on, so
  the eye lingers.

**Comment bait** — convert watchers into commenters (comments are a strong push signal *and* seed the
algorithm's "people can't stop engaging" read):
- **Ask a low-friction question the audience is dying to answer:** *"What's the one product YOU swear
  got smaller? I'll check the database and reply."* (On-brand: it literally feeds our pipeline — route
  answers to `/submit`.)
- **The "next victim" vote:** *"Comment the brand you want caught next."* — builds the series queue.
- **Lead-magnet variant (use sparingly, platform-dependent):** *"Comment CHECK and I'll DM you the
  full list."* High comment volume, but reads as growth-hacky; reserve for a deliberate growth push,
  not the default voice. Never promise a DM you can't deliver.

> **Gate reminder:** an interaction loop must never manufacture fake evidence to bait engagement. The
> receipt you ask them to pause on is **real** (three-bucket policy, `gates.md`). The pause is the
> trick; the data underneath is not.

---

## Worked example — a Reveal rewritten to the full spine

**Product:** Lay's 235 g → 145 g (−38%, same price). *(Trace to `approved-claims.md` before use.)*

```
[1 · HOOK  0–3s]      (text: "this bag is lying to you")
                      "This is the most shrunk snack in America right now —
                       and you bought it all summer."
[2 · AGITATE 3–8s]    "They never shrink what you eat alone. They shrink what you
                       bring to the cookout — because nobody weighs a party bag."
[3 · RE-HOOK 8–13s]   (HARD CUT → BeforeAfter overlay; camera rehook)
                       "Watch what happened to this exact bag in 18 months."
[4 · CONTEXT 13–22s]  "235 grams down to 145. That's 38% gone. Same bag, same shelf
                       price." (SourceFrame receipt flashes — pause bait)
[5 · BUILD 22–35s]    "And it's not just Lay's — Chex Mix, Tostitos, Nathan's, Honey
                       Maid, all cut the same week. That's the Generosity Tax: the
                       more you share, the more they skim."
[6 · PEAK-CUT 35–39s] "So next time someone says inflation's cooling — that bag is
                       38% emptier and nobody told you."  ← CUT. No outro.
CAPTION (CTA lives here): full 5-item list + "look any of these up free at
                       fullcarts.org" + "comment the product YOU want checked next"
                       + hashtags.
```

Compare to the flat version (`hook → list of 5 → "follow us"`): same data, but the spine adds the
agitation lock-in, a re-hook at the sag, a pause-bait receipt, a comment loop, and a peak-cut ending.

---

## The spine checklist (run alongside the hook checklist, every script)

```
[ ] RE-HOOK     a deliberate attention-reset at the ~30–45% sag (new question OR hard cut to receipt)
[ ] PEAK-CUT    spoken script ENDS on the payoff/number — no spoken "follow/link in bio"
[ ] CTA→CAPTION the ask (fullcarts.org, follow) is in the caption/end-card, not the VO
[ ] LOOP        an interaction loop present: pause-bait receipt, hidden second detail, OR comment ask
[ ] CURVE       no flat "list of N" middle — each beat opens or closes a loop
[ ] GATES       every on-screen number traces to approved-claims; pause-bait evidence is REAL
```

---

## Sources (credited, not ingested as VFX)

These are *script-strategy* talking-heads, not VFX effects, so they are **not** added to
`vfx_instructions/manuals/` (that store is for effect-recreation). Crediting here instead:

- **Jun Yuh** (`@jun_yuh`) — "script your videos like this to maximize your retention" —
  https://www.instagram.com/reel/DTg0_tkkXur/ — source of the 6-beat spine, the re-hook, and the
  peak-cut/loop ending.
- **Peter** (`@peter.visuals`) — "the algorithm just follows people" —
  https://www.instagram.com/reel/DXUUFoEDys_/ — source of the interaction-loop / replay-signal model
  ("every retry is another view") and the comment-bait lead-magnet mechanic.
