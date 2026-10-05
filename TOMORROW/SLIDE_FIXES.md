# SLIDE FIXES — what to change before you present

Faculty will see **only these 14 slides**. Fix the wording issues below, then you are defensible.

---

## FIX 1 — SLIDE 2 IS EMPTY (highest priority)

Slide 2 has **zero shapes** — no text, no image. If it appears on screen the audience sees a blank
white slide and it looks like a crash.

**Fix:** delete slide 2, OR set it to "hidden" (right-click → Hide Slide).

**Then note the split shifts.** With slide 2 gone, there are 13 slides and the speaking order
becomes: Member 1 = slides 1, 2, 3 · Member 2 = 4, 5, 6, 7, 8 · Member 3 = 9, 10, 11, 12, 13.
The SPEECH.md timings still apply to the same *content*, just renumbered.

---

## FIX 2 — FOOTER NUMBERS ARE WRONG

Footers read "2 / 11" through "11 / 11", but the deck has 14 slides. They counted only the speaking
slides and ignored the title and the two backups.

**Fix (optional, 2 minutes):** you can leave them — they are tiny grey text and nobody reads them.
**But** do not say "slide 8 of 11" out loud. If you want them right, the speaking slides should be
numbered 1–11 in presentation order.

---

## FIX 3 — SLIDES 5 AND 10 ARE LABELLED "Backup"

Both carry a visible "Backup" tag and both are labelled "MEMBER 1" (slide 5) and "MEMBER 3"
(slide 10). If you click through them, the audience sees "Backup" on screen.

**Fix:** hide both slides (right-click → Hide Slide). They stay available for Q&A. If a faculty
member asks about the spectra or the novelty diagram, you can jump to them.

---

## FIX 4 — CHECK THESE PHRASES FOR OVERCLAIM

I read every word on every slide. These are the phrases that could be attacked. Each has a safer
version — pick one and change it.

| Slide | Current wording | Risk | Safer wording |
|---|---|---|---|
| 3 | "File format and size alone separate the classes (AUROC 1.000)" | Medium — sounds like our detector got 1.000 | "The *original* files' format and size alone separate the classes (1.000)" |
| 6 | "Same processing for both classes" | **High** — slide 3 says each class was resized differently, so this contradicts it | "Same processing *steps* for both classes — but each class is resized by a different factor" |
| 9 | "Test AUROC (0.5 = chance)" | Low, keep | — |
| 11 | "Similar pooled score, different generator results" | Low, keep | — |
| 12 | "Which arm looks stronger?" | Medium — could be read as a claim | "Which arm scored higher? (interval spans zero under R)" |
| 14 | "A pooled score cannot tell you what simple features detect" | **High** — absolute wording | "A pooled score did not tell us what simple features detect *here*" |
| 14 | "the same pooled score hid per-generator changes of −0.17 to +0.30" | Low, accurate, keep | — |

**The two HIGH-risk ones (slide 6 and slide 14) are the ones to fix.** Everything else is defensible
as written.

---

## FIX 5 — SOURCE LINE ON SLIDE 9 IS INCOMPLETE

Slide 9 reads: `Source: results/*.csv, results/diagnostics/ (config)` — the config reference is
cut off. It should end with the hash.

**Fix:** make it `Source: results/*.csv, results/diagnostics/ (config 87f5489e9d59)`

---

## WHAT IS **NOT** OVERCLAIMED (do not "fix" these)

These are already correctly qualified. Leave them alone.

* Slide 4: "Exploratory reference-data check — BigGAN pixels unchanged; crop and training data
  change" — perfect. Do not remove the caveat.
* Slide 8: "E1–E5 were fixed in advance. R was added after the results: exploratory."
* Slide 11 footer: "Exploratory D1: 599 test images; crop, reference images and fitted models also
  change."
* Slide 12: "The interval does not establish spatial superiority" (in notes).
* Slide 13: every limitation is paired with a planned extension, and none is presented as done.

The deck is already more honest than most. Your job is to **not weaken it by speaking over it.**

---

## FINAL CHECKLIST (do these tonight)

- [ ] Delete or hide slide 2 (the empty one)
- [ ] Hide slides 5 and 10 (the backups)
- [ ] Fix slide 6 wording: "Same processing *steps*, but each class is resized differently"
- [ ] Fix slide 14 wording: soften "cannot" → "did not ... here"
- [ ] Fix slide 9 source line: add config hash
- [ ] Rehearse aloud, all three members, with a timer
- [ ] Agree who clicks, who holds the remote, who says "over to Member 2"
- [ ] Print SPEECH.md and the TIMING SHEET for each member
