# SFX slots (see src/FolgersReveal/Sfx.tsx + the style board sound table)

Drop sounds here with these exact names — the comp probes what exists and
skips missing slots, so partial sets are fine:

| slot | used for | spec |
|---|---|---|
| stamp.mp3 | CAUGHT cold-open (0.5s), EXCUSE slam (12s), PERMANENT RAISE (85.6s) | hard stamp / shutter-thunk — the sonic logo |
| roll.mp3 | 2,228 counter (21.2s) | fast odometer/counter roll |
| ding.mp3 | counter land (22s), fullcarts.org (97.4s) | soft ding/thunk |
| deflate.mp3 | after-bar shrink (44.5s) | short descending deflate |
| pop.mp3 | −14.7% badge (46.6s) | tight pop |
| tick.mp3 | highlight rings, arrow land, R&F chip | receipt-print / stamp tick |
| typing.mp3 | "stare at numbers all day" (18s) | subtle mechanical keyboard |
| whoosh.mp3 | cutaway transitions (in only) | clean low whoosh |
| whoosh-up.mp3 | rocket streak (75s) | short ascending whoosh — NOT a riser |
| thunk.mp3 | "on purpose" (36.2s), peak dot (54.8s) | low thunk |
| slide.mp3 | fall arrow draws (58s) | slow descending slide |
| tap.mp3 | end card (93.6s) | soft positive UI tap |
| drone.mp3 | underbed, loops, ducks out at 93.6s | low tense minimal drone |

Generate the stamp + counter in ElevenLabs SFX (text-to-SFX); the rest can
come from the Captions library. Keep them dry — levels are set in Sfx.tsx
(−12 to −18 dB equivalent under the voice).
