"""Final course presentation (v3, 2026-09-30): 13 slides, 3 members x 2 minutes, one framing.

Framing: "Same score, different story" - pooled AUROC hides that the images' resampling history decides
which generator looks easy and which feature family looks best.

Teacher guideline sections (tracker at the top of every slide):
  Introduction (2-3) - Novelty (4, highlighted) - Methodology (5-6, diagrams) - Experiments (7)
  - Results (8-11, tables/charts/matrices) - Limitations + Future (12)
Member split: M1 = 1-4, M2 = 5-8, M3 = 9-13. Slides stay light; the explanation is in the speaker notes.
Design system and helpers from build_presentation.py (Georgia/Arial, ink navy, one crimson accent).

Usage: python src/build_final_deck.py   (needs figures/final/ and figures/deck/; output: presentation/final_presentation.pptx)
"""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from build_presentation import (ACCENT, BODY, DARK, DISPLAY, HAIR, M, MUTED, PAPER, PRIMARY, ROOT, SH, SW,
                                TEXT, TINT, WHITE, add_slide, cell_border_bottom, figure, notes, set_cell,
                                textbox)

OUT = ROOT / "presentation" / "final_presentation.pptx"
FF, FD = ROOT / "figures" / "final", ROOT / "figures" / "deck"
TOTAL = 13
SECTIONS = ["Introduction", "Novelty", "Methodology", "Experiments", "Results", "Limitations", "Future"]
PIX, FRQ, CMB = RGBColor(0x2A, 0x78, 0xD6), RGBColor(0xEB, 0x68, 0x34), RGBColor(0x1B, 0xAF, 0x7A)
# same hues darkened for TEXT (>= 4.5:1 on white); the lighter marks stay for strokes, matching the figures
PIX_T, FRQ_T, CMB_T = RGBColor(0x1F, 0x63, 0xB8), RGBColor(0xB5, 0x48, 0x19), RGBColor(0x0E, 0x7A, 0x53)
ACC_TINT = RGBColor(0xFB, 0xEE, 0xF0)
SRC = "Source: results/*.csv, results/diagnostics/ (config 87f5489e9d59)"


# ------------------------------------------------------------------------------------------ helpers
def bg(s, color):
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    r.fill.solid(); r.fill.fore_color.rgb = color; r.line.fill.background()


def hdr(s, active, title, member):
    """Section tracker (current section in crimson) + title + member tag."""
    w = (SW - 2 * M) / len(SECTIONS)
    for i, name in enumerate(SECTIONS):
        on = i in active
        textbox(s, M + int(w * i), Inches(0.28), int(w), Inches(0.3), name.upper(), size=10.5, bold=on,
                color=ACCENT if on else MUTED, align=PP_ALIGN.CENTER)
        if on:
            u = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, M + int(w * i) + Inches(0.25), Inches(0.6),
                                   int(w) - Inches(0.5), Emu(28575))
            u.fill.solid(); u.fill.fore_color.rgb = ACCENT; u.line.fill.background()
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, M, Inches(0.62), SW - 2 * M, Emu(9525))
    ln.fill.solid(); ln.fill.fore_color.rgb = HAIR; ln.line.fill.background()
    textbox(s, M, Inches(0.78), Inches(10.3), Inches(0.6), title, size=27, bold=True, color=PRIMARY, font=DISPLAY)
    textbox(s, SW - M - Inches(1.5), Inches(0.9), Inches(1.5), Inches(0.3), member.upper(), size=11,
            bold=True, color=MUTED, align=PP_ALIGN.RIGHT)


def rich(s, x, y, w, h, runs, size=18, font=BODY, spacing=1.2, align=PP_ALIGN.LEFT):
    """One paragraph of mixed runs: (text, color, bold[, font]). Numbers go in BODY for lining figures."""
    tf = s.shapes.add_textbox(x, y, w, h).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment, p.line_spacing = align, spacing
    for t, color, bold, *f in runs:
        r = p.add_run()
        r.text = t
        r.font.size, r.font.color.rgb, r.font.bold, r.font.name = Pt(size), color, bold, (f[0] if f else font)


def flat(prs):
    """Drop the theme style reference from every auto shape and connector, so no renderer adds the theme's
    drop shadow; each shape already sets its own fill and line explicitly."""
    for sl in prs.slides:
        for sh in sl.shapes:
            st = sh._element.find(qn("p:style"))
            if st is not None:
                sh._element.remove(st)


def footer(s, n, dark=False):
    c = PAPER if dark else MUTED
    textbox(s, M, SH - Inches(0.38), Inches(9), Inches(0.26),
            "CSE 4883 Digital Image Processing  ·  Same score, different story", size=10, color=c)
    textbox(s, SW - M - Inches(1.4), SH - Inches(0.38), Inches(1.4), Inches(0.26), f"{n} / {TOTAL}", size=10,
            color=c, align=PP_ALIGN.RIGHT)


def box(s, x, y, w, h, lines, fill=WHITE, line=HAIR, lw=1.0, align=PP_ALIGN.CENTER,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    """lines: list of (text, size, bold, color)."""
    sh = s.shapes.add_shape(shape, x, y, w, h)
    sh.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.12
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line; sh.line.width = Pt(lw)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    for k, (t, size, bold, color) in enumerate(lines):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = t
        r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(size), bold, color, BODY
    return sh


def arrow(s, x1, y1, x2, y2, color=MUTED, w=1.75):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    c.line.color.rgb = color
    c.line.width = Pt(w)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))


def table(s, x, y, data, col_w, size=13, row_h=Inches(0.44), bold_cells=(), accent_cells=(), fill_rows=(),
          center_from=1):
    shp = s.shapes.add_table(len(data), len(data[0]), x, y, sum(col_w), row_h * len(data))
    t = shp.table
    for j, cw in enumerate(col_w):
        t.columns[j].width = cw
    for i, row in enumerate(data):
        t.rows[i].height = row_h
        for j, v in enumerate(row):
            c = t.cell(i, j)
            head = i == 0
            set_cell(c, v, size=size - (1 if head else 0), bold=head or (i, j) in bold_cells,
                     color=ACCENT if (i, j) in accent_cells else (MUTED if head else TEXT),
                     fill=TINT if head else (ACC_TINT if i in fill_rows else None),
                     align=PP_ALIGN.LEFT if j < center_from else PP_ALIGN.CENTER)
            cell_border_bottom(c)
    return shp


# ------------------------------------------------------------------------------------------ slides
def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH

    # 1 cover ---------------------------------------------------------------------------------
    s = add_slide(prs); bg(s, DARK)
    textbox(s, M, Inches(1.6), Inches(12), Inches(1.0), "Same score, different story", size=48, bold=True,
            color=WHITE, font=DISPLAY)
    textbox(s, M, Inches(2.75), Inches(12), Inches(1.1), "How resampling history shapes what spatial-frequency "
            "features\ndetect in AI-generated images", size=22, color=PAPER, spacing=1.1)
    textbox(s, M, Inches(5.35), Inches(12), Inches(1.2), "CSE 4883 Digital Image Processing  ·  final presentation\n"
            "Member 1  ·  Member 2  ·  Member 3", size=15, color=PAPER, spacing=1.35)
    textbox(s, M, Inches(6.55), Inches(12), Inches(0.4), "   ·   ".join(SECTIONS), size=11, color=PAPER)
    notes(s, "MEMBER 1 (10 s). Good morning. We studied what simple, explainable image statistics really "
             "measure when they separate real photographs from AI-generated images. Our title is our answer: "
             "the same score can tell very different stories.")

    # 2 introduction: the problem -------------------------------------------------------------
    s = add_slide(prs); hdr(s, [0], "Real and fake images arrive differently", "Member 1")
    figure(s, FD / "classes_at_native_scale.png", Inches(1.2), Inches(1.5), SW - Inches(2.4), Inches(4.55))
    rich(s, M, Inches(6.2), SW - 2 * M, Inches(0.8), [
        ("File format and size alone separate the classes (AUROC ", TEXT, False), ("1.000", ACCENT, True),
        ("). A fair pipeline gives every image 256 × 256 px, but ", TEXT, False),
        ("each class is resized by a different factor.", ACCENT, True)], size=17, align=PP_ALIGN.CENTER)
    footer(s, 2)
    notes(s, "MEMBER 1 (35 s). Simple features such as edge strength or spectral band energy are popular for "
             "spotting AI images because they are cheap and explainable. We used GenImage, a standard "
             "benchmark. Look at how its images arrive: real photos are JPEGs of varying size, and each "
             "generator gives PNGs of one fixed size: 128 pixels for BigGAN, 256 for ADM, 512 for Stable "
             "Diffusion. A classifier that only reads format and size already separates the classes perfectly. "
             "So a fair study must give every image the same size and format. But that means BigGAN is "
             "enlarged two times, Stable Diffusion is halved, and real photos are shrunk to about two thirds.")

    # 3 introduction: research question -------------------------------------------------------
    s = add_slide(prs); hdr(s, [0], "Our research question", "Member 1")
    box(s, Inches(2.2), Inches(1.6), Inches(8.9), Inches(0.95),
        [("Which simple feature set separates real from AI-generated images best?", 18, True, PRIMARY),
         ("same processing for both classes  ·  strict split by image group", 13, False, MUTED)], fill=TINT, line=TINT)
    xs = [Inches(1.4), Inches(5.2), Inches(9.0)]
    arms = [("Pixel-pattern", "7 features", PIX, PIX_T), ("Frequency", "7 features", FRQ, FRQ_T),
            ("Combined", "14 features", CMB, CMB_T)]
    for x, (a, b, c, ct) in zip(xs, arms):
        arrow(s, Inches(6.65), Inches(2.55), x + Inches(1.45), Inches(3.05))
        box(s, x, Inches(3.1), Inches(2.9), Inches(0.9), [(a, 17, True, ct), (b, 13, False, MUTED)], line=c, lw=2)
        arrow(s, x + Inches(1.45), Inches(4.0), Inches(6.65), Inches(4.45))
    box(s, Inches(4.4), Inches(4.5), Inches(4.5), Inches(0.62),
        [("one simple classifier for all three", 14, True, TEXT)], fill=TINT, line=TINT)
    arrow(s, Inches(5.6), Inches(5.12), Inches(3.6), Inches(5.6))
    arrow(s, Inches(7.7), Inches(5.12), Inches(9.7), Inches(5.6))
    box(s, Inches(1.4), Inches(5.62), Inches(4.4), Inches(0.9),
        [("Stress 1: matched JPEG", 16, True, PRIMARY), ("both classes at quality 90 / 75 / 50", 13, False, MUTED)],
        line=PRIMARY, lw=1.5)
    box(s, Inches(7.5), Inches(5.62), Inches(4.4), Inches(0.9),
        [("Stress 2: unseen generator", 16, True, PRIMARY), ("SD v1.4 never seen in training", 13, False, MUTED)],
        line=PRIMARY, lw=1.5)
    footer(s, 3)
    notes(s, "MEMBER 1 (30 s). Our question: with the same processing for both classes and a strict split, "
             "which simple feature set works best? We compare three sets: seven pixel-pattern features, seven "
             "frequency features, and all fourteen combined, each with the same simple classifier. Then we "
             "stress them in two realistic ways: JPEG compression applied equally to both classes, and a "
             "generator the classifier has never seen. Our goal is to measure what the features detect, not to "
             "build a new detector.")

    # 4 novelty (highlighted) -----------------------------------------------------------------
    s = add_slide(prs); bg(s, ACC_TINT); hdr(s, [1], "Novelty: same score, different story", "Member 1")
    rich(s, M, Inches(1.75), Inches(5.2), Inches(2.9), [
        ("Give every image the same resampling. The pooled AUROC barely moves (", TEXT, False, DISPLAY),
        ("0.796 → 0.802", PRIMARY, True), ("), but per-generator AUROC shifts by ", TEXT, False, DISPLAY),
        ("−0.17 to +0.30", ACCENT, True), (".", TEXT, False, DISPLAY)], size=24, spacing=1.25)
    rule_ = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, M, Inches(4.75), Inches(5.2), Emu(9525))
    rule_.fill.solid(); rule_.fill.fore_color.rgb = HAIR; rule_.line.fill.background()
    textbox(s, M, Inches(4.95), Inches(5.2), Inches(1.3),
            "BigGAN images are pixel-identical in both versions, so any change in BigGAN comes from the real "
            "photos' processing alone.", size=15, color=TEXT, spacing=1.2)
    data = [["Work", "Level", "What it varies"],
            ["Grommelt et al. 2024", "whole detector", "JPEG and size bias"],
            ["B-Free 2025", "whole detector", "content, format, size"],
            ["Zhou & Wang 2026", "training-free detectors", "resize vs native, JPEG"],
            ["This work", "14 named features", "resampling (isolated), matched JPEG, unseen generator"]]
    table(s, Inches(6.1), Inches(1.75), data, [Inches(1.6), Inches(1.9), Inches(3.13)], size=12.5,
          row_h=Inches(0.62), bold_cells={(4, 0), (4, 1), (4, 2)}, accent_cells={(4, 0), (4, 1), (4, 2)},
          center_from=9)
    textbox(s, Inches(6.1), Inches(5.3), Inches(6.63), Inches(0.6),
            "We found no report of this feature-level protocol; we say “not found”, not “first”.",
            size=13, color=MUTED, spacing=1.15)
    footer(s, 4)
    notes(s, "MEMBER 1 (45 s). This is our novelty. Earlier studies showed that whole detectors exploit format "
             "and size differences; one recent audit showed resizing changes the conclusions of training-free "
             "detectors. We go one level down, to fourteen named statistics, and we isolate the cause. When we "
             "give every image the same resampling history, the pooled score does not move, 0.796 before and "
             "0.802 after. But per generator, results move by minus 0.17 to plus 0.30. Same score, different "
             "story. We can pin the cause down because the BigGAN images are pixel-identical in both versions; "
             "only the real photos changed. Member 2 will explain how we built the study.")

    # 5 methodology: pipeline -----------------------------------------------------------------
    s = add_slide(prs); hdr(s, [2], "Pipeline, fixed before any image was processed", "Member 2")
    figure(s, ROOT / "src" / "pipeline-diagram.png", M, Inches(1.5), Inches(4.3), Inches(5.55))
    steps = [("3,000 GenImage images", "1,500 real  ·  500 each: BigGAN, SD v1.4, ADM"),
             ("Clean before splitting", "duplicates, near-copies, odd colour profiles removed"),
             ("Same processing for both classes", "resize to 256 × 256, lossless PNG"),
             ("Three conditions", "C0 clean  ·  C1 JPEG 90 / 75 / 50  ·  C2 unfair control"),
             ("Strict statistics", "split by image group  ·  one locked 600-image test set  ·  95% CIs")]
    for k, (a, b) in enumerate(steps):
        y = Inches(1.7 + 1.0 * k)
        c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.4), y, Inches(0.5), Inches(0.5))
        c.fill.solid(); c.fill.fore_color.rgb = PRIMARY; c.line.fill.background(); c.shadow.inherit = False
        c.text_frame.text = str(k + 1)
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        p.runs[0].font.size, p.runs[0].font.bold, p.runs[0].font.color.rgb = Pt(15), True, WHITE
        textbox(s, Inches(6.1), y - Inches(0.02), Inches(6.6), Inches(0.32), a, size=16, bold=True, color=TEXT)
        textbox(s, Inches(6.1), y + Inches(0.32), Inches(6.6), Inches(0.3), b, size=13, color=MUTED)
    footer(s, 5)
    notes(s, "MEMBER 2 (30 s). This is the pipeline we presented and had accepted, fixed before we processed any "
             "image. We sample 3,000 GenImage images, half real and half generated. Before splitting, we remove "
             "duplicates, near-copies and images with unusual colour profiles. Both classes then get exactly the "
             "same processing: 256 by 256 pixels, lossless PNG. From that we make three conditions: clean, "
             "JPEG at three qualities, and one deliberately unfair control. Every image group stays on one side "
             "of the split, and all experiments share one locked test set of 600 images.")

    # 6 methodology: features + classifier ----------------------------------------------------
    s = add_slide(prs); hdr(s, [2], "14 explainable features, one simple classifier", "Member 2")
    figure(s, FD / "feature_anatomy.png", M, Inches(1.45), SW - 2 * M, Inches(3.75))
    flow = [("14 features", "per image"), ("Standardise", "fit on train only"), ("Logistic regression", "L2, C chosen on val"),
            ("Threshold", "best val balanced acc."), ("Test AUROC", "+ 95% bootstrap CI")]
    bw, gap = Inches(2.15), Inches(0.35)
    for k, (a, b) in enumerate(flow):
        x = M + (bw + gap) * k
        box(s, x, Inches(5.5), bw, Inches(0.85), [(a, 15, True, PRIMARY), (b, 12, False, MUTED)],
            fill=TINT if k != 4 else WHITE, line=TINT if k != 4 else ACCENT, lw=1.5)
        if k < 4:
            arrow(s, x + bw + Inches(0.03), Inches(5.925), x + bw + gap - Inches(0.03), Inches(5.925))
    footer(s, 6)
    notes(s, "MEMBER 2 (30 s). Each image becomes fourteen numbers. The pixel arm, in blue, looks at brightness "
             "statistics, edge strength from the Sobel gradient, fine detail from the Laplacian, and a high-pass "
             "residual. The frequency arm, in orange, looks at the power spectrum: how energy splits between "
             "low, mid and high bands, the top band near the Nyquist limit, the slope of the fall-off, "
             "directionality, and single peaks. The bottom row is the classifier: one L2 logistic regression for "
             "every arm, tuned on validation data only, and scored by AUROC with confidence intervals.")

    # 7 experiments ---------------------------------------------------------------------------
    s = add_slide(prs); hdr(s, [3], "Experiments: what each one tests", "Member 2")
    data = [["", "Images", "Trained on", "Why it matters"],
            ["E1", "clean (C0)", "all 3 generators", "is there any signal?"],
            ["E2", "reals JPEG, fakes PNG", "all 3", "how an unfair pipeline cheats"],
            ["E3", "both JPEG 90 / 75 / 50", "all 3", "real images are compressed"],
            ["E4", "clean (C0)", "SD v1.4 held out", "a generator never seen"],
            ["E5", "JPEG 75", "SD v1.4 held out", "both stresses (headline)"],
            ["R", "same resampling for all", "as E1 and E4", "is it resampling history?"]]
    table(s, M, Inches(1.5), data, [Inches(0.6), Inches(2.25), Inches(1.9), Inches(2.85)], size=13.5,
          row_h=Inches(0.47), bold_cells={(i, 0) for i in range(1, 7)}, accent_cells={(6, j) for j in range(4)},
          fill_rows={6}, center_from=9)
    figure(s, FD / "jpeg_strip.png", M, Inches(5.1), Inches(7.6), Inches(1.85))
    textbox(s, Inches(8.5), Inches(1.55), Inches(4.25), Inches(0.3), "R: how every image is resampled", size=13.5,
            bold=True, color=ACCENT)
    rsteps = [("native image", "no resize"), ("crop 128 x 128", "native pixels"), ("enlarge 2x", "bicubic, all classes")]
    for k, (a, b) in enumerate(rsteps):
        y = Inches(2.0 + 0.78 * k)
        box(s, Inches(8.5), y, Inches(4.25), Inches(0.58), [(a, 14, True, TEXT), (b, 11.5, False, MUTED)],
            fill=WHITE, line=ACCENT if k == 2 else HAIR, lw=1.25)
        if k < 2:
            arrow(s, Inches(10.62), y + Inches(0.58), Inches(10.62), y + Inches(0.78))
    textbox(s, Inches(8.5), Inches(4.5), Inches(4.25), Inches(1.6),
            "E1–E5 were fixed in advance.\nR was added after the results: exploratory.\n"
            "BigGAN (128 px) is pixel-identical in C0 and R.", size=13, color=MUTED, spacing=1.2)
    footer(s, 7)
    notes(s, "MEMBER 2 (30 s). Each experiment answers one question. E1: is there any signal on clean images? "
             "E2 is the unfair control where only the reals are compressed. E3 compresses both classes equally; "
             "top right you see the same patch at each JPEG quality. E4 removes Stable Diffusion from training to "
             "test an unseen generator, and E5 adds JPEG on top; that was our planned headline. R, in red, is a "
             "diagnostic we added after the results: every image is cropped at native size and enlarged by the "
             "same factor, so all images share one resampling history.")

    # 8 results 1: accepted pipeline matrix + controls ----------------------------------------
    s = add_slide(prs); hdr(s, [4], "Results: combined wins pooled — not everywhere", "Member 2")
    figure(s, FD / "auroc_matrix.png", M, Inches(1.5), Inches(7.3), Inches(5.35),
           caption="Test AUROC (0.5 = chance). E5: SD v1.4 never seen in training, JPEG 75.", source=SRC)
    textbox(s, Inches(8.3), Inches(1.6), Inches(4.4), Inches(0.35), "Controls (every experiment)", size=15,
            bold=True, color=PRIMARY)
    ctr = [("Always guess", "0.500"), ("Processed-file history", "0.500"), ("Shuffled labels (×200)", "0.50–0.52"),
           ("Original file facts", "1.000")]
    for k, (a, b) in enumerate(ctr):
        y = Inches(2.1 + 0.52 * k)
        textbox(s, Inches(8.3), y, Inches(2.8), Inches(0.35), a, size=14, color=TEXT)
        textbox(s, Inches(11.2), y, Inches(1.5), Inches(0.35), b, size=14, bold=True,
                color=ACCENT if k == 3 else TEXT, align=PP_ALIGN.RIGHT)
    table(s, Inches(8.3), Inches(4.45), [["Stress", "AUROC change"],
                                        ["Matched JPEG, any arm", "at most 0.025"],
                                        ["SD v1.4 unseen, combined", "−0.078"]],
          [Inches(2.6), Inches(1.8)], size=13, row_h=Inches(0.48))
    footer(s, 8)
    notes(s, "MEMBER 2 (45 s). Here are the results of the accepted pipeline. The combined set has the best "
             "pooled score, 0.793, and stays best in every experiment. On the unseen generator under JPEG it "
             "reaches 0.629. JPEG compression barely changes the scores, and the unseen generator costs about "
             "0.08. The controls on the right pass: guessing, processed-file history and shuffled labels are at chance, while the original file facts separate perfectly, which is why identical processing matters. "
             "But look at the BigGAN column: almost perfect, 0.997 with frequency features, while the two "
             "diffusion generators stay between 0.58 and 0.71. Why is BigGAN so easy? Member 3 will show you.")

    # 9 results 2: radial spectra -------------------------------------------------------------
    s = add_slide(prs); hdr(s, [4], "Why BigGAN is easy: our resize empties its high band", "Member 3")
    figure(s, FD / "radial_spectra.png", M, Inches(1.5), SW - 2 * M, Inches(5.4),
           caption="Mean power spectrum per class, all images. Left: BigGAN, the only class enlarged 2x, loses energy "
                   "above 0.25 cycles/pixel. Right: with the same resampling for all, the three fake curves coincide.",
           source="Source: results/diagnostics/radial_spectra.csv")
    footer(s, 9)
    notes(s, "MEMBER 3 (30 s). This is the mechanism. The plot shows how much energy each class has at each "
             "spatial frequency. On the left, the accepted pipeline: BigGAN, in red, drops sharply in the high "
             "band, because it is the only class our resize enlarged, and bicubic enlargement cannot create fine "
             "detail. So high-frequency features find BigGAN almost perfectly, but they are detecting our resize, "
             "not the generator. On the right, every image gets the same resampling, and the three generators "
             "collapse onto one curve.")

    # 10 results 3: resampling swap -----------------------------------------------------------
    s = add_slide(prs); hdr(s, [4], "Same pooled score, different story", "Member 3")
    figure(s, FF / "fig_resampling_swap.png", M, Inches(1.45), SW - 2 * M, Inches(4.35))
    # before -> after, one row; each value in the text colour of the arm it belongs to (matches the figure)
    cols = [("Pooled  ·  combined arm", "0.796 → 0.802", CMB_T), ("BigGAN  ·  frequency arm", "1.000 → 0.828", FRQ_T),
            ("Unseen SD v1.4  ·  pixel arm", "0.477 → 0.771", PIX_T)]
    cw = (SW - 2 * M) / 3
    for k, (a, b, c) in enumerate(cols):
        x = M + int(cw * k)
        textbox(s, x, Inches(5.95), int(cw), Inches(0.3), a, size=12.5, color=MUTED, align=PP_ALIGN.CENTER)
        textbox(s, x, Inches(6.25), int(cw), Inches(0.5), b, size=24, bold=True, color=c, align=PP_ALIGN.CENTER)
    footer(s, 10)
    notes(s, "MEMBER 3 (35 s). Now the test. Open circles are the accepted pipeline, filled circles are the "
             "same-resampling version, on the same 599 test images. The pooled score does not move: 0.796 to "
             "0.802. But BigGAN falls from 1.000 to 0.828 with frequency features, even though its images did "
             "not change at all. Stable Diffusion rises, and on the unseen generator the pixel arm goes from "
             "chance to 0.771. On the right, the features that found BigGAN almost perfectly lose most of that "
             "power. Resampling explains the near-perfect BigGAN result, though not all of it: the spectral "
             "slope still separates.")

    # 11 results 4: effect sizes + ranking + JPEG decisions -----------------------------------
    s = add_slide(prs); hdr(s, [4], "Resampling moves results more than JPEG or shift", "Member 3")
    figure(s, FF / "fig_effect_sizes.png", M, Inches(1.45), Inches(5.9), Inches(5.45),
           caption="Each dot: one feature set on one generator; tick = pooled.")
    textbox(s, Inches(6.9), Inches(1.55), Inches(5.8), Inches(0.35), "Which arm looks stronger?  pixel − frequency",
            size=14.5, bold=True, color=PRIMARY)
    table(s, Inches(6.9), Inches(2.0), [["Pipeline", "AUROC difference [95% CI]"],
                                       ["Accepted resize", "−0.088 [−0.130, −0.045]"],
                                       ["Same resampling", "+0.022 [−0.015, 0.056]"]],
          [Inches(2.2), Inches(3.6)], size=13.5, row_h=Inches(0.5), accent_cells={(1, 1)})
    textbox(s, Inches(6.9), Inches(3.85), Inches(5.8), Inches(0.35), "JPEG q50 on the clean model: reals flagged as fake",
            size=14.5, bold=True, color=PRIMARY)
    table(s, Inches(6.9), Inches(4.3), [["Arm", "clean", "JPEG q50"],
                                       ["Pixel", "98 / 300", "157 / 300"],
                                       ["Frequency", "14 / 300", "16 / 300"],
                                       ["Combined", "37 / 300", "42 / 300"]],
          [Inches(2.2), Inches(1.8), Inches(1.8)], size=13.5, row_h=Inches(0.48), accent_cells={(1, 2)})
    footer(s, 11)
    notes(s, "MEMBER 3 (30 s). This chart compares all changes side by side. JPEG moves scores within about 0.1, removing a generator spreads them over 0.22, and changing only the resampling spreads them "
             "over 0.40. It even changes which feature family looks stronger: frequency beats pixel under the "
             "accepted resize, but the difference disappears with matched resampling. One practical warning "
             "from JPEG: the ranking barely changes, but a clean pixel model flags more than half of the "
             "compressed real photos as fake.")

    # 12 limitations → future ----------------------------------------------------------------
    s = add_slide(prs); hdr(s, [5, 6], "Limitations and planned extensions", "Member 3")
    pairs = [("R added after results; also narrows the field of view", "pre-specified native-resolution protocol (matched view)"),
             ("only SD v1.4 held out", "hold out each generator in turn"),
             ("real and fake content not matched", "content-matched real / fake pairs"),
             ("one JPEG encoder (Pillow 4:2:0)", "a second encoder and subsampling"),
             ("one dataset, one random split", "repeated splits and a second dataset")]
    textbox(s, M, Inches(1.55), Inches(5.3), Inches(0.35), "Limitation", size=15, bold=True, color=ACCENT)
    textbox(s, Inches(7.35), Inches(1.55), Inches(5.3), Inches(0.35), "Planned extension", size=15, bold=True,
            color=PRIMARY)
    for k, (a, b) in enumerate(pairs):
        y = Inches(2.0 + 0.92 * k)
        box(s, M, y, Inches(5.4), Inches(0.7), [(a, 14, False, TEXT)], fill=ACC_TINT, line=ACC_TINT,
            align=PP_ALIGN.LEFT)
        arrow(s, M + Inches(5.5), y + Inches(0.35), Inches(7.25), y + Inches(0.35), color=MUTED)
        box(s, Inches(7.35), y, Inches(5.4), Inches(0.7), [(b, 14, False, TEXT)], fill=TINT, line=TINT,
            align=PP_ALIGN.LEFT)
    footer(s, 12)
    notes(s, "MEMBER 3 (25 s). Our claims are bounded, and each limitation points to a planned extension. The "
             "resampling test was added after the results and also narrows the field of view, so next we would "
             "fix a native-resolution protocol in advance. We held out only one generator, the content of real "
             "and fake images is not matched, and we used one JPEG encoder, one dataset and one split. Each "
             "arrow is the step that removes that limitation.")

    # 13 closing ------------------------------------------------------------------------------
    s = add_slide(prs); bg(s, DARK)
    textbox(s, M, Inches(1.6), Inches(12), Inches(1.65),
            "A pooled score cannot tell you what\nsimple features detect.", size=36, bold=True, color=WHITE,
            font=DISPLAY, spacing=1.1)
    textbox(s, M, Inches(3.35), Inches(12), Inches(0.5), "Report resampling history, and report per generator.",
            size=20, color=PAPER)
    rich(s, M, Inches(4.45), Inches(11.5), Inches(1.0), [
        ("Combined features scored best pooled (", PAPER, False), ("0.793", WHITE, True),
        ("; ", PAPER, False), ("0.629", WHITE, True), (" on an unseen generator under JPEG 75), yet the same "
                                                          "pooled score hid per-generator changes of ", PAPER, False),
        ("−0.17 to +0.30", WHITE, True), (".", PAPER, False)], size=16, spacing=1.3)
    textbox(s, M, Inches(6.2), Inches(12), Inches(0.4), "Thank you  ·  questions?", size=18, bold=True,
            color=WHITE, font=DISPLAY)
    footer(s, 13, dark=True)
    notes(s, "MEMBER 3 (10 s). To conclude: combined features scored best, but a pooled score cannot tell you what "
             "simple features detect. Report the resampling history and report per generator. Thank you; we "
             "are happy to take questions.")

    flat(prs)
    OUT.parent.mkdir(exist_ok=True)
    prs.save(OUT)
    print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")


if __name__ == "__main__":
    build()
