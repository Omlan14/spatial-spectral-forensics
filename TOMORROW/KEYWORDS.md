# KEYWORDS — plain meanings of every hard word on the slides

If a faculty member uses one of these words, you should be able to answer. Read the "say this" line
if you forget the definition mid-sentence.

---

## MEASUREMENT WORDS

**AUROC** — how well the model puts all fake images above all real images in its ranking.
0.5 = random guessing. 1.0 = perfect. **Not accuracy, not a percentage.**
*Say:* "It measures ranking quality. Half means chance."

**Confidence interval** — a range around our number showing how much it could wiggle from sampling.
*Say:* "With only 600 test images, the number has noise. The interval shows that noise."

**Bootstrap** — the method we used to get that interval. We resample the test set with replacement
1,000 times and see how much the number moves.
*Say:* "We resample the test images 1,000 times to estimate the uncertainty."

**Group bootstrap** — same, but we resample whole image *groups*, so a picture and all its
processed copies move together.
*Say:* "We resample by original picture, not by individual file, to avoid duplicates."

**Balanced accuracy** — the average of "how many fakes we caught" and "how many reals we correctly
cleared." Useful when the two classes are unequal in size.

**Threshold** — the score above which we call an image fake. Chosen on validation data, never on
test.
*Say:* "The cut-off line. We set it on validation data so the test set stays untouched."

**Per-generator AUROC** — the score for one generator's fakes compared against *all* the real
images. This is what exposes what the pooled number hides.

**Pooled** — all generators mixed into one single number. This is what most papers report, and what
our project says is misleading on its own.

---

## IMAGE AND FEATURE WORDS

**Luminance** — the brightness version of a pixel, made by combining red, green and blue into one
number. We used the standard formula (0.299 R + 0.587 G + 0.114 B).
*Say:* "We convert to brightness only, so colour cannot give us a shortcut."

**Spatial feature** — a number measured directly on pixels. Example: variance = how spread out the
brightness values are.
*Say:* "Measured on the picture itself."

**Frequency feature** — a number measured on the picture's power spectrum, which says how much
detail sits at each scale.
*Say:* "Measured after converting to the frequency domain — how much fine versus coarse detail."

**Power spectrum** — the result of the Fourier transform. Shows how much energy sits at each
spatial scale. Low frequency = coarse shapes. High frequency = fine detail and edges.

**Band energy fraction** — the share of total energy inside a frequency band. We used three:
low (coarse), mid (texture), high (fine detail).

**Nyquist ratio (f11)** — how much of the high-band energy sits at the very top of the range. This
is the feature that flipped direction under JPEG, and it is the resize/JPEG tell.

**Spectral slope (f12)** — how fast energy falls as scale increases. Natural images follow a
roughly straight line in log space.

**Anisotropy (f13)** — whether detail is stronger in some directions than others.

**Peak concentration (f14)** — whether energy is spread out or bunched into a few spikes. This one
was the most stable under JPEG but carried no signal at all.

**Hann window** — a soft fade applied to the image edges before the Fourier transform, so the
border does not create fake frequencies.
*Say:* "A window that stops the edges of the image from producing artificial results."

**Laplacian** — a filter that measures how fast brightness is changing. It reacts strongly to sharp
detail, so it goes low when an image is blurry or enlarged.

**High-pass residual** — subtract a light blur from the image. What is left over is the sharp detail.

**Sobel gradient** — measures edge strength using neighbouring pixels.

**Downsampling / upsampling / resampling** — making an image smaller or bigger. Enlarging with
bicubic interpolation *smooths* the image and removes fine detail from the top of the frequency range.
This is the mechanism behind our main finding.

**Bicubic** — the specific interpolation method we locked for resizing. Chosen once, in advance.

---

## PIPELINE AND EXPERIMENT WORDS

**Pipeline** — the fixed sequence of steps our data goes through. Locked in writing before we
processed any image.

**Pre-registered / pre-specified** — we wrote down the whole plan, including the numbers we expected,
before running anything. **Not** the same as registering on a public website.

**Condition** — how the images were processed. C0 = clean. C1 = JPEG compressed. C2 = a deliberately
unfair control.

**Control check** — a cheap test that can *stop* the pipeline if something is wrong. It does not
improve results; it catches mistakes.

**Shortcut / leakage** — when the model can succeed for the wrong reason (e.g. reading file names)
instead of learning what we wanted.

**Exploratory vs confirmatory** — confirmatory = planned in advance. Exploratory = decided after
seeing results. Both are legitimate; they must be labelled honestly.

**Unseen generator / held out** — a generator completely removed from training, then tested. This
measures whether the method learned the generator or something more general.

**Stress test** — applying a realistic difficulty (compression, a new generator) to see if the
result holds.

**Deviation** — a documented, dated change to the locked plan. Ours: the shuffled-label control
changed from one shuffle to 200, with the reason recorded before the rerun.

**Image group** — one original picture plus every processed copy made from it. The split is done by
group, so copies of one picture can never sit on both sides of train and test.

---

## GENERATOR NAMES (just say what they are)

**BigGAN** — a GAN. Older style generator. Its images here are only 128 pixels, so our pipeline had
to enlarge them 2×. This is the source of most of our headline finding.

**Stable Diffusion v1.4 (SD v1.4)** — a diffusion model. Its images are 512 pixels, so our pipeline
shrank them. This is the "unseen generator" in our headline test.

**ADM** — a diffusion model too. Images are 256 pixels, so no resizing was needed. Convenient
control case.

**GenImage** — the public dataset we used. It has folders per generator, plus a folder of real
ImageNet photographs.

---

## THE HARDEST NUMBER TO EXPLAIN

**"What does your project actually contribute, in one sentence?"**

> We show that the number usually reported — one pooled score — can stay the same while individual
> generators change from nearly perfect to much worse, and that this happens because of how images
> were resized, not because of how they were generated. So the reporting rule should be: always
> report the resampling history, and always report per generator.

That is slide 14's message. Say it slowly. It is the sentence they will remember.

