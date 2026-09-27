# Literature Review — Spatial and Frequency Features for AI-Generated Image Detection

**Project:** Interpreting Spatial–Frequency Features for AI-Generated Image Detection Under Generator Shift and JPEG Compression
**Main research question:** With the same processing applied to both classes and a strict split by image group, which simple feature set separates real photographs from AI-generated images best: pixel-pattern features, frequency (spectrum) features, or both combined? And how much does the answer change when (a) both classes are JPEG-compressed, and (b) the test set uses a generator the study never trained on?
**Reference set:** 20 papers. Every paper here supports at least one design decision in `experimental-pipeline.md`. The bracketed numbers [1]–[20] are the project's citation numbers and are used the same way in the pipeline document and in `references.bib`.
**Date:** 2026-09-14 · **Status:** verified (see Section 2) · **Companions:** `experimental-pipeline.md`, `references.bib`

---

## 1. Purpose and scope

This review supports one study: a fair, feature-level comparison of three simple feature sets (pixel-pattern, frequency, and combined) for telling real photographs from AI-generated images, tested under JPEG compression and on an unseen generator. It is organized by **the job each paper does in that study**, not by citation count or fame.

Two decisions fixed the reference set:

1. **At most 20 references** (project scope decision).
2. **Every reference must have a job.** The set is the 17 papers that directly shape the design (Tier 1 and Tier 2 of the earlier ranking) plus the 3 most useful context papers with a stated role in the pipeline: DIRE [19] and FIRE [20] (the reconstruction family, cited as context and deliberately not implemented) and AI-GenBench [14] (the fallback data source). No paper is kept as decoration, and no paper is cited that the pipeline does not use.

**What this review is not:** it is not a systematic review and does not claim to cover everything. Every record was checked at the level of title, authors, and venue. No paper's full text or result tables were audited, and **no claim in this project depends on numbers we have not inspected.**

**How to read an entry.** Each numbered entry gives the verified reference, what the authors did, what they found, why the paper is in our study, and (where needed) how far we can use its result without overclaiming.

## 2. Verification status

All 20 records were verified on 2026-09-14 against primary sources: arXiv pages, CVF Open Access pages, publisher DOI pages (SciTePress, IEEE), the OpenReview API, and the OpenAlex index. Verification covered **titles, author lists, and venues**, not only links.

Corrections made during this check (compared with earlier drafts of this work):

| Record | Earlier draft said | Verified correct form | Evidence |
|---|---|---|---|
| Corvi et al. [12] | venue "AVSS 2023"; author list included F. Marra | **ICASSP 2023**; authors include **Koki Nagano**, not Marra | DOI 10.1109/ICASSP49357.2023.10095167; arXiv:2211.00680 |
| Durall et al. [7] | "CVPRW 2019" | **CVPR Workshops 2020** | CVF Open Access (CVPR 2020 workshops) |
| Wang et al. [11] | listed "P. Isola", who is not an author | **Sheng-Yu Wang, Oliver Wang, Richard Zhang, Andrew Owens, Alexei A. Efros** | arXiv:1912.11035 |
| Frank et al. [5] | last author "T. Horst" | **Thorsten Holz** | arXiv:2003.08685 |
| Guillaro et al. [2] | listed a co-author who does not exist | **F. Guillaro, G. Zingarini, B. Usman, A. Sud, D. Cozzolino, L. Verdoliva** | arXiv:2412.17671; CVF CVPR 2025 page |
| Tan et al. [16] | a co-author was missing | **C. Tan, H. Liu, Y. Zhao, S. Wei, G. Gu, P. Liu, Y. Wei** | arXiv:2312.10461; OpenAlex |
| Wang et al. [19] | two co-authors were missing | **Z. Wang, J. Bao, W. Zhou, W. Wang, H. Hu, H. Chen, H. Li** | arXiv:2303.09295; OpenAlex |
| Zhu et al. [13] | author list contained incorrect names | **M. Zhu, H. Chen, Q. Yan, X. Huang, G. Lin, W. Li, Z. Tu, H. Hu, J. Hu, Y. Wang** | arXiv:2306.08571; OpenAlex |
| Yan et al. [4] | author list did not match the record | **S. Yan, O. Li, J. Cai, Y. Hao, X. Jiang, Y. Hu, W. Xie** | arXiv:2406.19435; OpenReview (ICLR 2025 Poster) |

In total, this check fixed **eight incorrect author lists**, completed **three incomplete author lists** (Sato [10], Pellegrini [14], Chu [20]) from their primary records, and fixed two venue errors. The earlier draft contained several wrong author names, which is why the rule below applies. Any future addition to the reference set follows the same rule: **nothing is cited until its details are checked against a primary source.**

---

## 3. The 20 papers, by job in the study

### Group A — Dataset bias and controls: why fair conditions are required (4 papers)

These papers set up the problem this study is built around. On public datasets, differences in *processing* (compression, format, size) and in *content* between the real and generated classes can be learned instead of the real generative traces. Any feature comparison that ignores this measures the wrong thing.

**[1] Grommelt, Weiss, Pfreundt & Keuper — "Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets"** · ECCV 2024 Workshops (proceedings 2025) · [arXiv:2403.17608](https://arxiv.org/abs/2403.17608) · [DOI](https://doi.org/10.1007/978-3-031-92089-9_6)
*What they did:* looked systematically at the unfair differences that JPEG compression and image size introduce into generated-image datasets, using GenImage as the working example. They show that a detector can reach high accuracy by using these accidental differences, and they retrain detectors on corrected data to see what changes.
*What they found:* compression and size differences alone can look like detection evidence; removing them changes (and generally improves) how well a detector transfers to new generators.
*Why it is in our study:* it is the most on-topic paper for our procedure. It justifies the matched JPEG condition (C1), the deliberate mismatch control (C2), the per-file source record, and processing both classes exactly the same way. **How far we can use it:** their finding is at the detector level. Our contribution is the per-feature version of the same question: which individual statistics gain or lose separation when processing is matched or mismatched. We do not claim to have discovered the bias itself. A full read is required before any stronger novelty wording.

**[2] Guillaro, Zingarini, Usman, Sud, Cozzolino & Verdoliva — "A Bias-Free Training Paradigm for More General AI-generated Image Detection" (B-Free)** · CVPR 2025 · [arXiv:2412.17671](https://arxiv.org/abs/2412.17671) · [CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Guillaro_A_Bias-Free_Training_Paradigm_for_More_General_AI-generated_Image_Detection_CVPR_2025_paper.html)
*What they did:* built a training method that removes content, format, and size differences from AI-image detection, then trained detectors under it.
*What they found:* the authors show that leading published detectors rely heavily on these differences; removing them gives more general detectors.
*Why it is in our study:* it justifies recording each file's format, size, and known history, and the warning in our report that *the same final format does not mean the same history*: a real photograph that was JPEG-compressed before we received it stays affected after we save it as PNG. Only the file record can capture that.

**[3] Gye, Ko, Shon, Kwon & Kim — "SFLD: Reducing the Content Bias for AI-Generated Image Detection"** · WACV 2025 (Oral) · [arXiv:2502.17105](https://arxiv.org/abs/2502.17105) · [CVF](https://openaccess.thecvf.com/content/WACV2025/html/Gye_Reducing_the_Content_Bias_for_AI-Generated_Image_Detection_WACV_2025_paper.html)
*What they did:* studied content bias, where detectors use differences in *what is shown* in the image (and how the dataset was built) instead of generation traces, and proposed a controlled way to build data (TwinSynths-style pairs) that reduces it.
*What they found:* content bias measurably inflates detection scores; controlling how the data is built changes the conclusions.
*Why it is in our study:* it is the reason the content-bias question (H5) is **not tested** here. Answering it properly needs content-matched generation, which is out of scope for this project window. It is cited in the limitations paragraph.

**[4] Yan, Li, Cai, Hao, Jiang, Hu & Xie — "A Sanity Check for AI-generated Image Detection"** · ICLR 2025 (Poster) · [arXiv:2406.19435](https://arxiv.org/abs/2406.19435)
*What they did:* built a deliberately difficult test set (Chameleon) and showed that leading detectors, which score near-perfectly on common benchmarks, fail on hard synthetic images.
*What they found:* reported detection quality depends strongly on the data; easy benchmarks overstate real ability.
*Why it is in our study:* it is the caution behind our careful claims and our preference for testing on unseen data over headline accuracy. **How far we can use it:** it is not evidence about JPEG specifically; cite it for data difficulty only.

### Group B — Frequency evidence and its limits (6 papers)

The frequency feature set (features 8–14) stands on this line of work, and equally on its counter-evidence.

**[5] Frank, Eisenhofer, Schönherr, Fischer, Kolossa & Holz — "Leveraging Frequency Analysis for Deep Fake Image Recognition"** · ICML 2020 · [arXiv:2003.08685](https://arxiv.org/abs/2003.08685) · [PMLR v119](https://proceedings.mlr.press/v119/frank20a.html)
*What they did:* analysed GAN-generated images in the frequency domain, traced the differences to the upsampling steps inside generators, and tested simple classifiers built on those features.
*What they found:* generated and real images separate in frequency space, and the paper examines how these features behave compared with spatial ones and under compression.
*Why it is in our study:* it is the foundation of the frequency set: band energies, spectral slope, and the expectation that upsampling leaves measurable traces. It also supports the H3 idea that broad-spectrum statistics carry usable signal.

**[6] Dzanic, Shah & Witherden — "Fourier Spectrum Discrepancies in Deep Network Generated Images"** · NeurIPS 2020 · [arXiv:1911.06465](https://arxiv.org/abs/1911.06465)
*What they did:* compared the averaged Fourier spectra of generated and natural images and found characteristic differences, concentrated at high frequencies, that can be used for detection.
*What they found:* a systematic spectral signature exists across the generators of that period, mainly in the high-frequency range.
*Why it is in our study:* it is the closest method relative for our high-frequency statistics. It directly motivates the high-band energy fraction and the Nyquist-band energy ratio (features 10–11) and rules out any novelty claim about "using Fourier features" (which we do not make).

**[7] Durall, Keuper & Keuper — "Watch your Up-Convolution: CNN Based Generative Deep Neural Networks are Failing to Reproduce Spectral Distributions"** · CVPR Workshops 2020 · [arXiv:2003.01826](https://arxiv.org/abs/2003.01826) · [CVF](https://openaccess.thecvf.com/content_CVPR_2020/html/Durall_Watch_Your_Up-Convolution_CNN_Based_Generative_Deep_Neural_Networks_Are_CVPR_2020_paper.html)
*What they did:* showed that up-convolution layers do not reproduce the spectral distributions of natural images, with the difference visible in the high-frequency band, and explored whether training can correct it.
*What they found:* the spectral mismatch is a systematic byproduct of common generator designs, but it is not permanent.
*Why it is in our study:* it is the origin of the spectral-mismatch observation and the "not permanent" warning. That warning is exactly why our design measures features **under stress** instead of assuming the traces stay.

**[8] Zhang, Karaman & Chang — "Detecting and Simulating Artifacts in GAN Fake Images"** · IEEE WIFS 2019 · [arXiv:1907.06515](https://arxiv.org/abs/1907.06515) · [DOI](https://doi.org/10.1109/WIFS47025.2019.9035107)
*What they did:* connected specific generator operations (especially upsampling) to specific spectral artifacts, and simulated these artifacts to study detector behaviour.
*What they found:* artifact patterns trace back to concrete generation operations rather than being a generic "fake" signature.
*Why it is in our study:* it supports reading our frequency features as traces of generator operations (band ratios, slope, peak concentration) rather than as arbitrary numbers.

**[9] Dong, Kumar & Liu — "Think Twice Before Detecting GAN-Generated Fake Images From Their Spectral Domain Imprints"** · CVPR 2022 (pp. 7865–7874) · [CVF](https://openaccess.thecvf.com/content/CVPR2022/html/Dong_Think_Twice_Before_Detecting_GAN-Generated_Fake_Images_From_Their_Spectral_CVPR_2022_paper.html)
*What they did:* showed that spectral fingerprints can be reduced or altered during generation, which hurts detectors that rely on them.
*What they found:* the spectral trace can be weakened, so detectors that assume it is always present are fragile.
*Why it is in our study:* it is the **counter-evidence that makes the JPEG test and the mismatch control mandatory rather than optional**. Any finding of "the frequency features separate the classes" from E1 is reported under this caution until E3 and E5 show what survives.

**[10] Sato, Yamashita, Fujiyoshi & Hirakawa — "Frequency-Domain Detection of AI-Generated Images via Radial Spectrum Templates"** · VISAPP 2026 · [DOI](https://doi.org/10.5220/0014250800004084)
*What they did:* built a spectrum template from real images only, and classified a test image by how far its radial spectrum deviates from that template. No generated images are used for training, and the decision is a simple threshold.
*What they found:* the method is competitive with deep baselines on GenImage, stays interpretable, and (because it trains on real images only) works across generators without retraining.
*Why it is in our study:* it is the closest recent comparison for our frequency set and the tightest limit on our novelty. **How far we can use it:** a full read is required before any stronger novelty wording. Our contribution is the joint procedure, not radial statistics themselves, which are not new.

### Group C — Generator dependence and data at scale (4 papers)

These papers establish that generator shift is a measured phenomenon and provide the dataset this study uses.

**[11] Wang, Wang, Zhang, Owens & Efros — "CNN-Generated Images Are Surprisingly Easy to Spot… for Now"** · CVPR 2020 · [arXiv:1912.11035](https://arxiv.org/abs/1912.11035)
*What they did:* showed that CNN-generated images across many models can be detected with simple classifiers and limited data, and studied what breaks that: JPEG compression at test time, and transfer to models not seen in training.
*What they found:* "easy to spot… for now": both the drop under compression and the fragility across generators are real, measured effects, and how the data is handled strongly affects the conclusions.
*Why it is in our study:* it covers both stresses of our study in one paper, motivating matched compression (C1) and unseen-generator testing (E4/E5), and supporting careful data handling in the split design.

**[12] Corvi, Cozzolino, Zingarini, Poggi, Nagano & Verdoliva — "On the Detection of Synthetic Images Generated by Diffusion Models"** · ICASSP 2023 · [arXiv:2211.00680](https://arxiv.org/abs/2211.00680) · [DOI](https://doi.org/10.1109/ICASSP49357.2023.10095167)
*What they did:* tested detectors trained on GAN-era artifacts against diffusion-model images and described the artifacts each family leaves.
*What they found:* GAN-trained detectors get substantially worse on diffusion outputs; the two families leave different artifacts (for example, the GAN-style grid is absent in diffusion images).
*Why it is in our study:* generator shift is a measured, published effect. This justifies holding out one entire family in E4/E5 and including one GAN family plus two diffusion families in the locked generator set.

**[13] Zhu, Chen, Yan, Huang, Lin, Li, Tu, Hu, Hu & Wang — "GenImage: A Million-Scale Benchmark for Detecting AI-Generated Image"** · NeurIPS 2023 Datasets and Benchmarks Track · [arXiv:2306.08571](https://arxiv.org/abs/2306.08571)
*What they did:* built a million-scale benchmark covering several generator families, with evaluation tasks designed for cross-generator generalization and degraded images.
*What they found:* cross-generator and degraded-image evaluation is practical at scale. The paper itself warns that a downloaded subset is not automatically free of unfair differences.
*Why it is in our study:* it is our data source, and we take its warning literally: our source check and matched conditions exist because a GenImage subset still carries whatever processing history its files arrived with [1].

**[14] Pellegrini, Cozzolino, Pandolfini, Maltoni, Ferrara, Verdoliva, Prati & Ramilli — "AI-GenBench: A New Ongoing Benchmark for AI-Generated Image Detection"** · IJCNN 2025 (Verimedia workshop) · [arXiv:2504.20865](https://arxiv.org/abs/2504.20865) · [DOI](https://doi.org/10.1109/IJCNN64981.2025.11228377)
*What they did:* designed a benchmark that adds new generators over time and evaluates detectors on the newly added, unseen ones.
*What they found:* testing against generators that were genuinely unseen is the right procedure for this field, and it has to be repeated as generators change.
*Why it is in our study:* it is the fallback data source in our access plan and further support that unseen-generator testing is the standard, not an unusual choice.

### Group D — Pixel-pattern statistics and classifier design (3 papers)

**[15] Nataraj, Mohammed, Chandrasekaran, Flenner, Bappy, Roy-Chowdhury & Manjunath — "Detecting GAN Generated Fake Images using Co-occurrence Matrices"** · Electronic Imaging 2019 · [arXiv:1903.06836](https://arxiv.org/abs/1903.06836)
*What they did:* described images by counting local pixel-value patterns (co-occurrence matrices) and classified them with a CNN.
*What they found:* local pixel statistics, a purely spatial representation, carry useful signal for GAN images.
*Why it is in our study:* it is the precedent for our pixel-pattern set: local statistics (our gradient, Laplacian, and high-pass features) are a small, explainable representation. **How far we can use it:** their classifier is a CNN, so we cite the *representation*, not the pipeline; our classifier is deliberately the simple one [17].

**[16] Tan, Liu, Zhao, Wei, Gu, Liu & Wei — "Rethinking the Up-Sampling Operations in CNN-Based Generative Network for Generalizable Deepfake Detection" (NPR)** · CVPR 2024 · [arXiv:2312.10461](https://arxiv.org/abs/2312.10461)
*What they did:* showed that upsampling leaves traces in the relationships between neighbouring pixels, and built a detector on that representation, tested across generators.
*What they found:* local pixel-relationship statistics transfer across generator families better than artifact-specific cues.
*Why it is in our study:* it is the modern anchor for the pixel-pattern set, the learned counterpart of our features, and the reason we expect this set to carry real signal in E1 rather than acting as a straw man.

**[17] Ojha, Li & Lee — "Towards Universal Fake Image Detectors that Generalize Across Generative Models" (UniversalFakeDetect)** · CVPR 2023 · [arXiv:2302.10174](https://arxiv.org/abs/2302.10174)
*What they did:* showed that a frozen pretrained representation (CLIP ViT) with a *simple* classifier (nearest neighbour or linear) generalizes across generators better than detectors trained end to end.
*What they found:* with fixed features, keeping the classifier simple is a feature, not a limitation: it measures the representation instead of mixing in training effects.
*Why it is in our study:* it is the methodological basis for our design: **fixed features plus one simple classifier, identical across the three feature sets.** The classifier is the measuring instrument; the features are what we study.

### Group E — Reconstruction-based context: cited, deliberately not implemented (3 papers)

These methods are an important part of the modern detection landscape and belong to a different cost class. They are cited as related work and are the reason our scope statement says "not a comparison against the best published methods".

**[18] Ricker, Lukovnikov & Fischer — "AEROBLADE: Training-Free Detection of Latent Diffusion Images Using Autoencoder Reconstruction Error"** · CVPR 2024 · [arXiv:2401.17879](https://arxiv.org/abs/2401.17879)
*What they did:* detected latent-diffusion images without training any detector, by measuring how well the images are reconstructed by a diffusion autoencoder.
*What they found:* generated images are reconstructed more faithfully by their own model family's autoencoder, which is a training-free signal from the generator side.
*Why it is in our study:* it shows detection is possible without training a detector, and it clarifies why reconstruction methods are context for us rather than baselines: they need parts of the generator itself, which is outside a small-feature study.

**[19] Wang, Bao, Zhou, Wang, Hu, Chen & Li — "DIRE for Diffusion-Generated Image Detection"** · ICCV 2023 · [arXiv:2303.09295](https://arxiv.org/abs/2303.09295)
*What they did:* measured how differently an image is reconstructed by a pretrained diffusion model (this difference is called DIRE) and used it as a detection signal.
*What they found:* diffusion-generated images show lower reconstruction error than real photographs under diffusion inversion, and this transfers across diffusion models.
*Why it is in our study:* it is the standard reconstruction-discrepancy method, cited so that our boundary is explicit: small features, one simple classifier, and no access to generator internals.

**[20] Chu, Xu, Wang, Zhang, You & Zhou — "FIRE: Robust Detection of Diffusion-Generated Images via Frequency-Guided Reconstruction Error"** · CVPR 2025 · [arXiv:2412.07140](https://arxiv.org/abs/2412.07140) · [DOI](https://doi.org/10.1109/CVPR52734.2025.01197)
*What they did:* combined frequency guidance with reconstruction error to make diffusion-image detection more robust.
*What they found:* frequency information improves reconstruction-based detection, and the combined pipeline is robust across the settings tested in the paper.
*Why it is in our study:* it is the most recent member of the reconstruction family and the clearest example of the cost class we do not enter: it combines frequency analysis with generator-side reconstruction, while we measure frequency statistics directly and alone.

---

## 4. What the papers support, hypothesis by hypothesis

**H1: first check.** Simple frequency statistics separate generated from camera images [5], [6], [7], [8], and the family remains competitive in recent form [10]; pixel-pattern statistics carry related signal [15], [16]. No paper we found establishes a *universal winner between feature sets under one fair procedure*. That comparison is our first-check table, and it is not a novelty claim.

**H2: shortcut check.** Strongly supported at the detector level: JPEG and size differences distort datasets [1]; content, format, and size differences are easy shortcuts [2], [3]; hard examples break detectors [4]; compression lowers artifact-based detection [11]. Our contribution here is at the feature level: which *individual* statistics gain or lose separation when processing is matched or mismatched. Grommelt et al. [1] report detector-level behaviour, not per-feature results.

**H3: broad vs narrow frequency features.** Plausible, **not settled**. Broad-spectrum features have an early robustness precedent [5], and spectral traces are known to be weakenable [9]. The design therefore splits the verdict in two (how much feature values change, and whether classification still works) and defines in advance which features count as broad (8–11, 13) and narrow (14).

**H4: generator dependence.** Confirmed as a phenomenon: GAN-trained detectors get worse on diffusion outputs [12], cross-generator transfer is a measured fragility [11], and benchmark design treats unseen-generator testing as standard [13], [14]. With three generator families and one locked fold, we measure transfer for *those* families only, with no claim of universality.

**H5: content dependence.** Documented as a real effect [3], [2], but testing it properly needs content-matched construction that this project does not run. Stated as untested in the limitations.

## 5. What is already known, and what this study adds

**Already established (not our claim):** frequency-domain traces and their use as detection features [5], [6], [7], [8]; radial spectrum templates [10]; local pixel-pattern statistics [15], [16]; simple classifiers on fixed features [17]; fairness controls in dataset design [1], [2], [3]; unseen-generator testing [12], [13], [14]; reconstruction-based detection [18], [19], [20].

**What this study adds (careful, limited claim):** a joint comparison at the feature level: same parent images, same classifier, three small feature sets (pixel-pattern, frequency, combined), tested under matched JPEG compression **and** on an unseen generator, with per-feature effect sizes and per-feature changes reported separately from classification results, plus control checks that catch leakage and rules fixed in advance.

**Required phrasing:** "no retrieved abstract reports this exact protocol", never "first" and never "state of the art". Before any stronger novelty wording in a paper submission, two papers must be read in full: Grommelt et al. [1] (closest JPEG-bias study) and Sato et al. [10] (closest radial-spectrum method). No other full-text reads are required by this plan.

## 6. Reference-set decisions

- **Included:** all Tier 1 and Tier 2 papers (17) plus the 3 Tier-3 papers with stated roles in the pipeline: DIRE [19], FIRE [20], and AI-GenBench [14].
- **Not included:** 17 further papers from the earlier merged corpus (field surveys, more learned detectors, face-forgery work, augmentation-shortcut studies, and alternative benchmarks). They are kept in `references.bib` in an archived section, marked as not cited, so future scope expansions can start from them. The rule applies to them too: nothing is cited until its details are checked against a primary source. Earlier drafts of this project contained several wrong author lists and two wrong venues, which is why the rule exists; Section 2 records every correction found.

**Citation key map (review number to `references.bib` key):**

| # | Key | # | Key | # | Key | # | Key |
|---|---|---|---|---|---|---|---|
| 1 | `grommelt2024fake` | 6 | `dzanic2020fourier` | 11 | `wang2020cnn` | 16 | `tan2024npr` |
| 2 | `guillaro2025bfree` | 7 | `durall2020watch` | 12 | `corvi2023detection` | 17 | `ojha2023universal` |
| 3 | `gye2025sfld` | 8 | `zhang2019artifacts` | 13 | `zhu2023genimage` | 18 | `ricker2024aeroblade` |
| 4 | `yan2025sanity` | 9 | `dong2022think` | 14 | `pellegrini2025aigenbench` | 19 | `wang2023dire` |
| 5 | `frank2020leveraging` | 10 | `sato2026radial` | 15 | `nataraj2019cooccurrence` | 20 | `chu2025fire` |
