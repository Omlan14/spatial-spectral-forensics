# DEFENSE Q&A — every likely attack and the answer

**Rules for tomorrow.** Answer in this order: (1) the short answer, (2) the number, (3) the honest
limit. **Never** say "first", "state of the art", "proved", or "caused" unless the slide says it.
If you do not know, say *"That was outside what we measured, so we cannot say."* That answer scores
well. Making something up does not.

---

## PART A — ATTACKS ON THE MAIN CLAIM (expect these first)

**Q1. "Your headline number is 0.629. That's barely better than a coin flip. Why should we care?"**
Because 0.629 is not our best number — it is our *honest worst case*. Combined features score 0.793
when every generator is seen in training. The 0.629 is what happens on a generator the model never
saw, under JPEG 75. We report the weak number because it is the realistic one. Our contribution is
not the score; it is showing *why* the score is weak.

**Q2. "So is this a good detector or a bad one?"**
We are not presenting a detector. We are presenting a measurement study. Our finding is that simple
features separate these images partly because of how the images were processed, not only because
they were generated. That is a reason to be careful with reported scores, including ours.

**Q3. "You say combined is best. But on BigGAN, frequency alone (0.997) beats combined (0.990)."**
Correct, and we say so on slide 9's title — "combined wins pooled, not everywhere." Combined wins
on the pooled number in every locked experiment. On individual generators it does not always win.
We report both because the pooled number is what papers usually show, and it hides this.

**Q4. "Isn't 0.793 just detecting that real photos are JPEGs and fakes are PNGs?"**
That is exactly the risk, and it is why we built control check 2. After our pipeline standardises
everything, a classifier reading only the analysed files' format and size gets **0.500**. So our
numbers are not coming from file names. But — and this is the honest part — standardising removes the
file facts, not their effect on the pixels. So we cannot fully rule it out. That is limitation 2.

---

## PART B — ATTACKS ON METHOD AND DESIGN

**Q5. "Why logistic regression? Why not a deep model?"**
Deliberately. The classifier is our measuring instrument, not our contribution. If we used a deep
network and got 0.95, we would not know which measurement caused it. A simple classifier keeps the
question answerable: *which of these 14 measurements carries the signal?* Adding deep baselines was
listed as out of scope before we saw results.

**Q6. "Why only 14 features? Feels arbitrary."**
They were fixed in writing before any data was processed. Seven spatial (variance, skew, kurtosis,
gradient, Laplacian, high-pass) and seven frequency (three band energies, Nyquist ratio, spectral
slope, anisotropy, peak). Each one was verified against a hand calculation on synthetic images
before we touched real data.

**Q7. "Why 3,000 images? Is that enough?"**
It was set in advance: 1,500 real and 500 from each of three generators. More would be better, but
the count was locked before results to avoid tuning. The bootstrap intervals on our slides show the
uncertainty we actually have.

**Q8. "You split 60/20/20. Why is the test set only 600 images?"**
600 parent images — 300 real and 100 per generator. We split by *image group*, meaning every
processed copy of one picture stays on one side of the split. Without that, a JPEG version of a
training image could appear in test and inflate the score. All experiments share the same 600 test
images, so every comparison we make is paired.

**Q9. "You changed a control check after it failed. Isn't that cheating?"**
This is the most important question, so here is the full honest answer.
Our first run stopped because a *single* shuffled-label run gave 0.623 instead of ~0.5. We stopped,
as our rules require. We then investigated and found **no indexing error** — features and labels
were correctly paired. We found that a single shuffle is just one random direction in a
14-dimensional space; the spread across 200 shuffles has a standard deviation of about 0.09. So one
shuffle simply cannot be used as a pass/fail gate.
We changed the check to 200 shuffles and gated on the mean, **before** the rerun, with the reason
written into our config file as a dated deviation. No feature, split, classifier or metric changed.
The final control gives 0.503–0.521. We would rather report this than hide it.

**Q10. "Your control 'original file facts' gives 1.000. Doesn't that invalidate everything?"**
It shows the *dataset* has a shortcut, not that our pipeline used it. That is why we ran it — to
expose the problem rather than be caught by it. After standardisation, file-facts give 0.500. We
report 1.000 openly on slide 9.

---

## PART C — ATTACKS ON THE EXPLORATORY DIAGNOSTIC (R)

**Q11. "You changed the crop AND the resampling AND retrained. How can you blame resizing?"**
You cannot, and we do not. Our slide says exactly this: "crop, reference images and fitted models
also change." What we can say is narrower and still useful: BigGAN's own 500 images are
pixel-identical in both conditions, so for the univariate feature comparison the change must come
from the real-image side. And the pooled score barely moves while per-generator scores move a lot.
That is enough for our conclusion, which is about *reporting*, not about causation.

**Q12. "Then what does R actually prove?"**
That the result is **sensitive to processing**. Not that resizing is the only cause. Our closing
slide says "report resampling history and report per generator" — a reporting rule, not a causal
claim.

**Q13. "You call R exploratory. Why should we believe it at all?"**
Because it is clearly labelled everywhere — on slide 8 ("R was added after the results:
exploratory"), on slide 11's footer, and in our notes. The main E1–E5 results are separate and
confirmatory. Exploratory does not mean unreliable; it means we did not plan it in advance.

**Q14. "Why 599 test images in R instead of 600?"**
Six real images were too small to crop at native resolution, so they were excluded. 2,994 parents
remained. That is also why R's baseline is 0.796 and not 0.793 — different image set. **Never mix
the two baselines.**

---

## PART D — ATTACKS ON THE JPEG CLAIM

**Q15. "You say JPEG changed almost nothing (0.025). But compression obviously damages images."**
Two different questions. AUROC measures *ranking* — the order of the images. That barely moved.
But decisions changed a lot: with the clean model and threshold fixed, spatial false positives rose
from 98/300 to 157/300 at quality 50. So ranking was stable while decisions were not. That is
slide 12's whole point.

**Q16. "Why did E3 refit the model at each quality? That hides the damage."**
E3 was designed to answer "does the recipe still work after compression," and refitting is correct
for that question. It cannot answer the transfer question. That is a known limitation (number 8),
and it is exactly why we added the fixed-model diagnostic. Both are reported.

**Q17. "Is the JPEG result encoder-specific?"**
Yes, and we say so. We used one encoder — Pillow, 4:2:0 chroma subsampling. Slide 13 lists "a
second encoder and subsampling" as a planned extension. We make no claim beyond the encoder we used.

---

## PART E — ATTACKS ON NOVELTY AND SCOPE

**Q18. "What is new here? Someone must have done frequency analysis on fake images before."**
Yes, and we cite them — our reference set has 20 verified papers. What we could not find in any
retrieved abstract is a study that traces processing history through *named individual features*,
*per-generator scores*, and *decision thresholds* together. Our wording is "no retrieved abstract
reports this exact protocol." **Never say "first" or "novel" as an absolute.**

**Q19. "Why not compare against an actual detector like CLIP or a FreGAN model?"**
Out of scope, declared in advance. Those are a different cost class — learned detectors and
reconstruction methods. Adding them would bury the contribution, which is about understanding
measurements, not winning a benchmark.

**Q20. "Only one dataset. Isn't that a fatal flaw?"**
It limits us, yes, and slide 13 lists it first among the planned extensions. Our claims are
explicitly scoped to GenImage's validation folders with three generators and one JPEG encoder.

**Q21. "You only held out one generator. 'Generator shift' is a big claim."**
Agreed — we never make the general claim. We say separation fell for Stable Diffusion when it was
held out. One fold describes one family. Slide 13 lists "hold out each generator in turn."

**Q22. "Real and fake images have different content. Isn't that the whole result?"**
It could be part of it, and we did not test it. That is hypothesis H5 in our plan, marked "not
tested by design" because it needs content-matched pairs. It is limitation 5, and slide 13 lists
"content-matched real / fake pairs" as planned work. **Never claim content is ruled out.**

**Q23. "Why no colour features, or LBP, or phase?"**
Removed in a scope reduction before results. Colour was dropped partly because we work on luminance
only. LBP and phase features were judged to duplicate information already in the two arms.


---

## PART F — THE NUMBERS THEMSELVES

**Q24. "What exactly is AUROC?"**
How well the model ranks all fake images above all real images. 0.5 means pure chance — it ranks
randomly. 1.0 means perfect separation. **It is not accuracy and not percent.** It does not depend
on the threshold, which is why we report it separately from decision counts.

**Q25. "What are the confidence intervals for?"**
The test set is only 600 images, so any single number has sampling noise. The intervals come from
1,000 rounds of bootstrap, resampling whole image *groups*. When an interval includes 0.5, we say
the result is not above chance. When it includes 0, we say there is no detectable change.

**Q26. "0.465 is below 0.5. Doesn't that mean your model is worse than random?"**
It means slightly worse than chance on that one subset, and the interval 0.410–0.527 includes 0.5,
so we describe it as "not above chance" rather than "worse than random." With 400 images, a small
deviation like this is normal noise.

**Q27. "You say spatial is at chance on unseen Stable Diffusion, yet combined beats frequency by
0.061. How is that possible?"**
Good question — we have checked it. At the threshold, spatial flags 34 of the 100 unseen fakes and
frequency flags 19, but they flag **different images**: together they catch 41, and 59 are missed by
both. So the two sets of features carry partly separate information, and the combined model can use
both. We do not claim to know which feature causes the gain.

**Q28. "Where does 0.793 come from and where does 0.629 come from — which is the real result?"**
Both are real, different questions. 0.793 is E1: every generator seen in training, clean images.
0.629 is E5: Stable Diffusion never seen in training, plus JPEG 75. E5 is our headline because it
is the harder and more realistic case.

**Q29. "Your D1 baseline is 0.796 but slide 9 says 0.793. Is one of them wrong?"**
No — different image sets. D1 drops 6 undersized images, so its baseline is 599 images (0.796).
Slide 9 is the locked 600-image test set (0.793). Both are correct for what they measure.

---

## PART G — MISCELLANEOUS TRAPS

**Q30. "Is this reproducible?"**
Yes. Every result table carries the config hash, the code version, and both seeds. We reran the
pipeline from the stored raw sample and reproduced every table. The hash is on slide 9.

**Q31. "Did you preregister this anywhere public?"**
No. We locked the specification in our repository before running, and committed each protocol before
its experiment. That is advance specification, not public preregistration. We describe it as
"pre-specified," never as externally registered.

**Q32. "Why is there a branch called `native-biggan-256`? Doesn't that mean you did the
never-enlarge test?"**
No — that branch points at the same commit as main. It contains no unique experiment. The
never-enlarge comparison is a planned extension, not a result. **Do not present it as done.**

**Q33. "Why does BigGAN behave so differently?"**
Because BigGAN is the only class that starts at 128 pixels and gets enlarged 2×. ADM starts at 256
and SD at 512. Enlarging an image leaves very little energy at the top of the frequency range, which
is exactly what several of our frequency features measure. So those features find BigGAN almost
perfectly — but that is measuring our resize, not the generator.

**Q34. "Could the difference just be the crop, not the resampling?"**
That is a fair objection and we cannot fully separate them — R changes both. Our defensible statement
is the narrow one: BigGAN's images are unchanged, so in the univariate comparison the change comes
from the real-image distribution. Resizing alone is not isolated, and slide 13's first row says so.

**Q35. "Your title says 'same score, different story.' Isn't that oversold?"**
It refers to one specific measurement: pooled combined goes 0.796 → 0.802 while BigGAN frequency
goes 1.000 → 0.828 and unseen-SD spatial goes 0.477 → 0.771. Similar pooled number, very different
per-generator stories. We do not claim the pooled score is always useless — only that in this case
it hid the effect.

---

## PART H — THE FIVE SENTENCES TO MEMORISE

If you remember nothing else, remember these. They cover most questions.

1. "We are not presenting a detector. We are presenting a measurement study."
2. "Our headline 0.629 is our honest worst case, not our best number."
3. "Combined wins pooled — but not on every generator, and we report both."
4. "We cannot separate resizing from cropping in R, so we call it sensitivity, not cause."
5. "Exploratory means we planned it after seeing results — not that it is unreliable."

---

## PART I — EMERGENCY ANSWERS

**"I don't know."** → *"That was outside what we measured, so we cannot say."* Then stop.

**"Can you show me the code?"** → *"Yes, it is in the project repository, and every result table
carries the config hash and code version."*

**"Was this published?"** → *"No, this is a course project. Our 20-paper reference set is verified
against primary sources."*

**"Which is the best detector you tested?"** → *"We did not test detectors. We tested three feature
sets with one simple classifier, because the question was which measurement carries the signal."*

**"Would you deploy this?"** → *"No. On an unseen generator under JPEG 75 the best arm reaches 0.629,
which is not enough to deploy. Our contribution is the reporting rule, not a deployable model."*

