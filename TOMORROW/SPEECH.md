# SPEECH SCRIPT — 3 members, 6 minutes

**Deck:** `presentation/final_presentation_rehearsal_updated.pptx` (14 slides)
**Split you asked for:** Member 1 = slides 1–4 · Member 2 = slides 5–9 · Member 3 = slides 10–14

## READ THIS FIRST — 3 things that will go wrong

1. **Slide 2 is EMPTY.** It has no text and no picture. If it shows on screen, the audience sees a
   blank white slide. **Either delete slide 2, or start Member 2 on slide 3 and shift the split.**
   Everything below assumes you keep slide 1 as the title, then speak from slide 3.
2. **Slides 5 and 10 say "Backup" on them.** They are extra material. If you speak them you will run
   out of time. The timings below SKIP them. Just click past them quickly.
3. **The footer numbers do not match the slide positions.** The footers say "2 / 11" to "11 / 11",
   but there are 14 slides. That is because footers counted only the 11 speaking slides. **Do not
   read the footer numbers out loud.** Nobody in the audience can see them anyway.

### Which slide belongs to whom (given slide 2 must be skipped)

| Member | Speaks slides | Time |
|---|---|---|
| Member 1 | 1 (title), 3, 4 | ~110 s |
| Member 2 | 6, 7, 8, 9 — *skip 5 (backup)* | ~110 s |
| Member 3 | 11, 12, 13, 14 — *skip 10 (backup)* | ~110 s |

Total speech = 330 s. Three handovers = 30 s. **Total = 6:00 exactly.** No slack. Rehearse aloud.

---

# MEMBER 1 — slides 1, 3, 4 (about 110 seconds)

### Slide 1 — title (about 10 seconds)

> Good morning. We are a group of three, and our project is on detecting computer-generated images
> using simple image-processing measurements.
>
> Our title is: same score, different story.

### Slide 3 — real and fake images arrive differently (about 45 seconds)

> We used 3,000 images from a public dataset called GenImage.
>
> Half of them are real photographs. The other half were made by three computer programs —
> BigGAN, Stable Diffusion, and ADM.
>
> Here is the first thing we found. The real photographs arrive as JPEG files, in different sizes.
> The computer-made pictures arrive as PNG files, all in fixed sizes. So just by looking at the
> file name and the size, we could tell real from fake perfectly. You can see the number one
> zero zero zero on the slide.
>
> We wanted every image to be the same size, so we made all of them 256 by 256 pixels. But here is
> the problem. To do that, we had to make some images bigger and some images smaller. BigGAN
> pictures are small, so we made them two times bigger. Stable Diffusion pictures are large, so we
> made them smaller.
>
> So although every image ended up the same size, each class was resized by a different amount.
> Making sizes equal did not remove the history of how the pictures were made.

### Slide 4 — what our project contributes (about 55 seconds)

> So what is our contribution?
>
> Previous work has shown this kind of problem at the level of the whole detector. Our project looks
> one level lower, at the level of individual features.
>
> Our contribution is a feature-level processing audit. That means we trace what happens to each
> individual measurement — through the features, through the per-generator scores, and through the
> actual decisions the classifier makes.
>
> We look at three groups of established questions. First, compression history — we know JPEG
> compression leaves marks. Second, benchmark comparability — the content, the format, and the size
> can differ between the classes. Third, resizing history — what happens when an image is resized
> versus kept at its native size.
>
> We then go one level down again, and look at fourteen named features. We ask which measurement
> moves, and for which generator.
>
> We ran two stresses under one fixed protocol: matched JPEG compression, and a generator the model
> never saw during training.
>
> We also ran an exploratory check on reference data. In it, BigGAN pixels stay identical while the
> real-image comparison changes. I must be honest that the crop and the training data also change
> there, so it is not a pure test of resizing alone.
>
> Member two will now explain the pipeline and the planned results.

---

# MEMBER 2 — slides 6, 7, 8, 9 (about 110 seconds)

### Slide 6 — the pipeline (about 25 seconds)

> Our pipeline was fixed in writing before we processed a single image.
>
> Step one: 3,000 GenImage images — 1,500 real, and 500 from each of the three generators.
>
> Step two: we cleaned the data before splitting. We removed duplicates, near-copies, and images
> with unusual colour profiles.
>
> Step three: we applied the same processing to both classes — resize to 256 by 256, save as
> lossless PNG.
>
> Step four: three conditions. C0 is clean. C1 is JPEG at quality 90, 75, and 50. C2 is an unfair
> control, used only to test the pipeline.
>
> Step five: strict statistics. We split by image group, so copies of one picture can never appear
> in both training and test. All experiments share one locked test set of 600 images. We report 95
> percent confidence intervals.

### Slide 7 — the features and the classifier (about 30 seconds)

> We use 14 simple, explainable features — 7 spatial and 7 frequency.
>
> The spatial features measure brightness, edge strength, and fine detail. For example, the
> Laplacian measures how quickly the brightness changes, which reacts to sharp detail.
>
> The frequency features come from the power spectrum — how much energy sits at each scale. We
> divide it into bands. Think of it as splitting the picture into coarse, medium, and fine detail,
> and measuring how much energy is in each.
>
> We deliberately kept these simple. If a complex model works, we cannot tell which measurement is
> responsible. Our goal is to understand the measurement itself.
>
> All three feature sets use the same simple classifier — logistic regression. Standardisation is
> fitted on training data only. The model setting and the decision threshold come from validation
> data only. We report AUROC, where one half means chance.

### Slide 8 — the experiments (about 25 seconds)

> Here is what each experiment tests.
>
> E1 is the clean baseline — is there any signal at all?
>
> E2 is the shortcut control. We deliberately give the real images JPEG and the fake images PNG. If
> the pipeline were cheating, this would show it.
>
> E3 applies the same JPEG quality to both classes — the fair compression test.
>
> E4 holds Stable Diffusion out of training entirely.
>
> E5 combines that holdout with JPEG 75. This is our headline result.
>
> R is our later diagnostic. We crop every image at its native size, then enlarge everything by the
> same amount.
>
> I must stress one point. E1 to E5 were fixed in advance. R was added after we saw the results, so
> it is exploratory. And BigGAN, being 128 pixels, is pixel-identical in both conditions.

### Slide 9 — the results (about 30 seconds)

> Here are the results. The vertical axis is AUROC, where one half is chance.
>
> Combined features give the best pooled score. In the clean baseline it is 0.793.
>
> But on Stable Diffusion — a generator never seen in training, under JPEG 75 — the same combined
> set reaches only 0.629, with a confidence interval from 0.571 to 0.690. Frequency alone is 0.568.
> Spatial alone is 0.465, which is not above chance.
>
> So combined wins. But notice the title of this slide: not everywhere.
>
> On the right are our control checks. Always-guess gives 0.500. File history in the matched
> conditions gives 0.500, so our pipeline is not reading file names. Shuffled labels give 0.50 to
> 0.52, so there is no indexing mistake. But original file facts give 1.000 — that is the dataset
> problem I mentioned, and we report it rather than hide it.
>
> Member three will explain why that difference matters.

---


# MEMBER 3 — slides 11, 12, 13, 14 (about 110 seconds)

### Slide 11 — similar pooled score, different generator results (about 40 seconds)

> This slide is the heart of our project.
>
> Our exploratory diagnostic compares the same 599 test images under two conditions. The original
> pipeline, and the native crop with a shared enlargement.
>
> Look at the pooled combined score. It goes from 0.796 to 0.802. Almost nothing.
>
> Now look at the individual generators. BigGAN, using frequency features, falls from nearly one to
> 0.828. Unseen Stable Diffusion, using spatial features, rises from 0.477 to 0.771.
>
> So the pooled number barely moves, but underneath it, one generator became much harder and
> another became much easier.
>
> And here is the important honesty point. BigGAN's own images do not change at all between the two
> conditions — they are pixel-identical. But the crop changes, and the training data changes, and we
> retrain. So we cannot say resizing alone caused this. We can only say the result is sensitive to
> processing, and that a pooled score cannot show it.

### Slide 12 — processing changes scores and decisions (about 35 seconds)

> There is a second warning on this slide.
>
> In the original pipeline, frequency features clearly beat spatial features. Under our diagnostic,
> that advantage disappears. But I want to be careful — the interval does not prove spatial features
> became better. It only means we can no longer claim frequency is clearly ahead.
>
> The second table is about decisions, not ranking. We took the clean model and its threshold, and
> did not retrain. Then we compressed the test images to JPEG 50.
>
> For the spatial arm, real images wrongly flagged as fake rose from 98 out of 300 to 157 out of
> 300. Frequency barely moved, 14 to 16. Combined moved 37 to 42.
>
> So a model can keep its ranking almost unchanged while its actual decisions get much worse. Similar
> AUROC does not guarantee similar decisions.

### Slide 13 — limitations and planned extensions (about 25 seconds)

> We also want to be clear about our limits.
>
> Our resampling diagnostic was designed after we knew the main results, so it is exploratory. It
> also changes the crop, not only the resizing. The fix is to fix the field of view first, then
> compare processing.
>
> Only Stable Diffusion was held out. The fix is to hold out each generator in turn.
>
> Real and fake content is not matched, so part of the separation may come from content. The fix is
> content-matched pairs.
>
> We used one JPEG encoder. The fix is a second encoder.
>
> And we used one dataset and one split. The fix is repeated splits and a second dataset.
>
> These are planned tests. They are not results.

### Slide 14 — conclusion (about 10 seconds)

> Our conclusion.
>
> Simple features do separate these images. But what they measure depends on how the images were
> processed.
>
> So we should always report the resampling history, and always report per generator.
>
> Thank you. We are happy to take questions.

---

# TIMING SHEET (print this)

| # | Slide | Who | Seconds | Running |
|---|---|---|---|---|
| 1 | 1 title | M1 | 10 | 0:10 |
| 2 | 3 arrive differently | M1 | 45 | 0:55 |
| 3 | 4 contribution | M1 | 55 | 1:50 |
| — | handover | | 10 | 2:00 |
| 4 | 6 pipeline | M2 | 25 | 2:25 |
| 5 | 7 features | M2 | 30 | 2:55 |
| 6 | 8 experiments | M2 | 25 | 3:20 |
| 7 | 9 results | M2 | 30 | 3:50 |
| — | handover | | 10 | 4:00 |
| 8 | 11 pooled vs generator | M3 | 40 | 4:40 |
| 9 | 12 scores and decisions | M3 | 35 | 5:15 |
| 10 | 13 limitations | M3 | 25 | 5:40 |
| 11 | 14 conclusion | M3 | 10 | 5:50 |
| — | buffer | | 10 | 6:00 |

**If you are running late, cut in this order:** slide 7 (features) → slide 13 (limitations) →
slide 4 (contribution). Never cut slides 9, 11, 12 or 14 — those carry the results and the honesty.

