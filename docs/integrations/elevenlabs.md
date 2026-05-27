# ElevenLabs API Integration

Text-to-speech for the social video pipeline (Remotion voiceovers). See
`docs/plans/2026-05-13-social-content-engine.md` for the content engine and
`docs/plans/2026-05-25-data-access-and-protection.md` for the secret-handling
stance this follows.

## The key itself is NOT stored in this repo

The secret lives in an environment variable, never in a tracked file. Set it as:

```
ELEVENLABS_API_KEY=<the secret>
```

Put that value in **one** of:
- The Claude Code web environment's secret / env-var settings (persists across
  the ephemeral container — the right home for automated runs). See
  https://code.claude.com/docs/en/claude-code-on-the-web.
- A gitignored `.env` in the Remotion / content-pipeline project (local dev).
  `.env` and `web/.env*.local` are already in `.gitignore`.

Read it in code via `process.env.ELEVENLABS_API_KEY` (Node) — never hardcode.

## Key configuration (set when the key was created)

| Setting | Value | Why |
|---|---|---|
| Plan | Pro, 160k credits/month | ~200 finished videos of audio; budget is not the constraint |
| Scope: Text to Speech | **Access** | The core job — script text → voiceover |
| Scope: Voices | **Read** | Reference voice IDs; cannot modify the voice library |
| All other scopes | **No Access** | Least privilege — no workspace/member/admin reach |
| Monthly credit cap | ~50k credits | Financial circuit-breaker against a runaway/looping render |

Optional scopes to add later if needed: Sound Effects (Access) and Music
Generation (Access) for generated background beds; Pronunciation Dictionaries
(Read) to fix tricky brand-name pronunciation (e.g. Mondelez).

## Credit budgeting

- ~1 credit/char on premium (multilingual v2); ~0.5 credit/char on Turbo/Flash.
- One 22–30s short ≈ 700–900 chars of VO ≈ ~800 credits final (premium).
- The cost driver is **regeneration** while tuning (5–10× early, ~2× once
  templated), not final renders. Draft on Turbo, finalize on premium.
- At the current ~8–10 videos/month cadence, expect ~20–40k credits/month used.

## Rotating / revoking

Manage keys in the ElevenLabs dashboard under Settings → API Keys. Because the
key is scoped and capped, it can be revoked and reissued freely. **Rotate
immediately if the value is ever pasted into a chat, log, commit, or shared
file**, then update the `ELEVENLABS_API_KEY` env var with the new value.
