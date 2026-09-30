"""Final course presentation v2 (16:9) - redesigned per the official pptx skill design rules.

Design system:
  Palette (BACKGROUND -> PRIMARY -> ACCENT): white content surfaces, deep ink navy for the
  cover/closing sandwich, spectral navy primary, one crimson accent used sparingly.
  Type pairing: Georgia for display (titles, oversized numerals, stat callouts) - academic serif;
  Arial for body, labels, captions, tables. Set explicitly on every run.
  Motif: oversized muted section numeral (top right) + hairline-ruled rows/frames. No accent
  bars, no title underlines, no filled card grids (banned AI-slide tells).
  Every figure slide: hairline frame, 12pt caption, 12pt source line.
  Teacher guideline: Introduction / Novelty (highlighted) / Methodology (diagrams) / Experiments
  (relevance) / Results (tables + charts, not raw text) / Limitations / Future extensions;
  ~2-minute speaker scripts per member in the notes.

Usage: python src/build_presentation.py   (output: to_human/final_presentation.pptx)
"""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "to_human" / "final_presentation.pptx"

BG = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x14, 0x21, 0x2E)
PRIMARY = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0xB2, 0x18, 0x2B)
TEXT = RGBColor(0x1C, 0x28, 0x33)
MUTED = RGBColor(0x5D, 0x6D, 0x7E)
HAIR = RGBColor(0xD5, 0xDB, 0xDB)
TINT = RGBColor(0xF2, 0xF5, 0xF8)
NUM = RGBColor(0xE3, 0xEA, 0xF1)
PAPER = RGBColor(0xAB, 0xB7, 0xC4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SW, SH = Inches(13.333), Inches(7.5)
M = Inches(0.6)
DISPLAY, BODY = "Georgia", "Arial"


def add_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _style(p, size, bold, color, italic, font, align, spacing):
    p.alignment = align
    if spacing:
        p.line_spacing = spacing
    for r in p.runs:
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = font


def textbox(slide, x, y, w, h, text, size=16, bold=False, color=TEXT, align=PP_ALIGN.LEFT,
            italic=False, font=BODY, spacing=None, anchor=None):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    if anchor:
        tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        _style(p, size, bold, color, italic, font, align, spacing)
    return box


def rows(slide, x, y, w, items, size=16, gap=Inches(0.18), rule=True, lead_color=PRIMARY,
         body_color=TEXT, sub_color=MUTED, line_h=Inches(0.62)):
    """Container-free row list: bold lead-in phrase + muted sub-line, hairline rules between."""
    cy = y
    for i, (lead, sub) in enumerate(items):
        textbox(slide, x, cy, w, Inches(0.34), lead, size=size, bold=True, color=lead_color)
        cy += Inches(0.30)
        if sub:
            box = textbox(slide, x, cy, w, line_h, sub, size=size - 3.5, color=sub_color,
                          spacing=1.05)
            cy += line_h
        if rule and i < len(items) - 1:
            ln = slide.shapes.add_shape(1, x, cy + Inches(0.02), w, Emu(9525))
            ln.fill.solid()
            ln.fill.fore_color.rgb = HAIR
            ln.line.fill.background()
            cy += gap
    return cy


def header(slide, title, kicker=None, dark=False):
    if kicker:
        textbox(slide, M, Inches(0.42), SW - 2 * M - Inches(2.45), Inches(0.3), kicker.upper(),
                size=11.5, bold=True, color=ACCENT if not dark else PAPER, font=BODY)
    textbox(slide, M, Inches(0.72), SW - 2 * M - Inches(2.45), Inches(0.75), title, size=29,
            bold=True, color=WHITE if dark else PRIMARY, font=DISPLAY)


def numeral(slide, n):
    textbox(slide, SW - M - Inches(2.2), Inches(0.18), Inches(2.2), Inches(1.5), n, size=88,
            bold=True, color=NUM, font=DISPLAY, align=PP_ALIGN.RIGHT)


def footer(slide, n, total, dark=False):
    c = PAPER if dark else MUTED
    textbox(slide, M, SH - Inches(0.42), Inches(7), Inches(0.28),
            "What do simple features measure in AI-generated image detection?", size=10.5, color=c)
    textbox(slide, SW - M - Inches(1.4), SH - Inches(0.42), Inches(1.4), Inches(0.28),
            f"{n} / {total}", size=10.5, color=c, align=PP_ALIGN.RIGHT)


def figure(slide, path, x, y, max_w, max_h, caption=None, source=None):
    """Fit the image inside (max_w, max_h minus the caption block); caption and source stack
    in one text box below, so they can never overlap. (x, y, max_w, max_h) is the whole
    content region and must end above the footer."""
    with Image.open(path) as im:
        iw, ih = im.size
    ar = iw / ih
    cap_h = Inches(0.68) if caption else Emu(0)
    img_area_h = max_h - cap_h
    w, h = int(max_w), int(max_w / ar)
    if h > img_area_h:
        w, h = int(img_area_h * ar), int(img_area_h)
    left, top = int(x + (max_w - w) / 2), int(y + (img_area_h - h) / 2)
    pic = slide.shapes.add_picture(str(path), left, top, w, h)
    pic.line.color.rgb = HAIR
    pic.line.width = Pt(0.75)
    if caption:
        ty = top + h + Inches(0.12)
        box = slide.shapes.add_textbox(x, ty, max_w, cap_h)
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p1 = tf.paragraphs[0]
        p1.text = caption
        p1.alignment = PP_ALIGN.CENTER
        _style(p1, 12, False, MUTED, False, BODY, PP_ALIGN.CENTER, 1.05)
        if source:
            p2 = tf.add_paragraph()
            p2.text = source
            p2.alignment = PP_ALIGN.CENTER
            _style(p2, 12, False, MUTED, False, BODY, PP_ALIGN.CENTER, 1.05)
    return pic


def stat(slide, x, y, number, label, w=Inches(4.2), color=ACCENT, num_size=60, label_size=13):
    textbox(slide, x, y, w, Inches(num_size / 60.0), number, size=num_size, bold=True,
            color=color, font=DISPLAY)
    textbox(slide, x, y + Inches(num_size / 60.0 * 1.02), w, Inches(0.55), label, size=label_size,
            color=MUTED, spacing=1.05)


def set_cell(cell, text, size=13.5, bold=False, color=TEXT, fill=None, align=PP_ALIGN.LEFT,
             font=BODY):
    cell.margin_left = cell.margin_right = Inches(0.12)
    cell.margin_top = cell.margin_bottom = Inches(0.06)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    else:
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    for r in p.runs:
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font


def cell_border_bottom(cell, color="D5DBDB", width_pt=0.75):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tag = qn("a:lnB")
    for old in tcPr.findall(tag):
        tcPr.remove(old)
    ln = tcPr.makeelement(tag, {"w": str(int(width_pt * 12700)), "cap": "flat"})
    fill = ln.makeelement(qn("a:solidFill"), {})
    clr = fill.makeelement(qn("a:srgbClr"), {"val": color})
    fill.append(clr)
    ln.append(fill)
    # insert before any fill element to keep schema order (ln*, fill*)
    tcPr.insert(0, ln)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH
    figs, ext = ROOT / "figures", ROOT / "figures" / "extended"
    TOTAL = 17

    # 1 cover (dark)
    s = add_slide(prs)
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background()
    textbox(s, M, Inches(1.95), Inches(11.5), Inches(2.2),
            "What do simple features measure\nin AI-generated image detection?",
            size=40, bold=True, color=WHITE, font=DISPLAY, spacing=1.05)
    textbox(s, M, Inches(4.15), Inches(11.5), Inches(0.5),
            "A controlled test under JPEG compression and unseen generators",
            size=19, color=PAPER)
    textbox(s, M, Inches(6.05), Inches(11.5), Inches(0.9),
            "Digital Image Processing - final presentation\nPre-registered study - config 87f5489e9d59 - 3,000 GenImage parents - experiments E1-E5",
            size=13, color=PAPER, spacing=1.25)
    notes(s, "Opening line (all members): Good morning. Our project asks one question: when simple, "
             "explainable features tell real photos from AI-generated images apart, what are they actually "
             "measuring - the generator, or the processing history of the files? We answered it with a "
             "pre-registered experiment on 3,000 images from GenImage, under matched JPEG compression and "
             "with one generator held out of training. Seven minutes total, one topic per member.")

    # 2 roadmap
    s = add_slide(prs)
    header(s, "Seven topics, one per member", kicker="How we split the guideline")
    items = [("01", "Introduction", "the trust problem in AI-image detection"),
             ("02", "Novelty", "three findings no retrieved abstract reports"),
             ("03", "Methodology / architecture", "locked pipeline, 14 features, four controls"),
             ("04", "Experiments", "E1-E5: what each test is for"),
             ("05", "Results analysis", "where the signal lives, what survives - tables and charts"),
             ("06", "Limitations", "what our claims do not cover"),
             ("07", "Future extensions", "three planned pre-registered next steps")]
    y = Inches(1.72)
    for i, (num, topic, desc) in enumerate(items):
        is_nov = topic == "Novelty"
        textbox(s, M, y, Inches(0.7), Inches(0.45), num, size=20, bold=True,
                color=ACCENT if is_nov else NUM, font=DISPLAY)
        textbox(s, M + Inches(0.85), y, Inches(5.4), Inches(0.35), topic, size=16.5, bold=True,
                color=ACCENT if is_nov else TEXT, font=DISPLAY if is_nov else BODY)
        textbox(s, Inches(6.7), y + Inches(0.04), Inches(5.3), Inches(0.35), desc, size=13,
                color=MUTED)
        textbox(s, Inches(12.15), y + Inches(0.04), Inches(0.6), Inches(0.3), "2 min", size=11.5,
                color=MUTED, align=PP_ALIGN.RIGHT)
        if i < len(items) - 1:
            ln = s.shapes.add_shape(1, M, y + Inches(0.56), SW - 2 * M, Emu(9525))
            ln.fill.solid(); ln.fill.fore_color.rgb = HAIR; ln.line.fill.background()
        y += Inches(0.665)
    footer(s, 2, TOTAL)
    notes(s, "Handover slide (member 1, ten seconds): Here is how we split the guideline topics. Each "
             "member takes one block for at most two minutes. The novelty block is the one to remember; "
             "everything else supports it. Put the presenter names next to the numbers before presenting.")

    # 3 introduction
    s = add_slide(prs)
    header(s, "Detectors can learn the wrong thing", kicker="Member 1 - Introduction")
    numeral(s, "01")
    rows(s, M, Inches(1.85), Inches(7.3), [
        ("Benchmarks score high",
         "often for the wrong reason"),
        ("File history is a perfect shortcut",
         "reals: JPEG photos, many sizes  -  fakes: fixed-size PNGs"),
        ("The open question",
         "which statistics inflate, and what survives fair processing?"),
    ], size=16.5, line_h=Inches(0.95))
    stat(s, Inches(8.6), Inches(2.15), "1.000", "AUROC of a classifier that sees only the original\n"
         "file facts (format, size, history) in every one\nof our experiments\n\nSource: results/control_checks.csv",
         w=Inches(4.1), num_size=64)
    footer(s, 3, TOTAL)
    notes(s, "Member 1, about two minutes: Simple frequency and pixel statistics are the classic cues for "
             "spotting AI-generated images. Spectral peaks and band energies come from generator upsampling; "
             "gradient and high-pass statistics come from pixel patterns. The problem is that datasets "
             "differ between the two classes in more than the generator. Real photos arrive as JPEG files "
             "of many sizes; generated images arrive as fixed-size PNGs. A detector can score well on that "
             "file history alone, without seeing generation at all. Documented at the detector level by "
             "Grommelt and by B-Free. On the right is our own number: a classifier that sees only the "
             "original file facts reaches AUROC 1.000 - perfect separation from metadata. So our question: "
             "under one fair procedure, which simple features really separate the classes, and what are "
             "they measuring? Hand over to the novelty block.")

    # 4 novelty (highlighted)
    s = add_slide(prs)
    header(s, "What this study adds", kicker="Member 2 - Novelty (highlighted)")
    numeral(s, "02")
    claims = [("1", "Per-feature verdicts, split in two",
               "value stability vs classification separation - each with confidence intervals"),
              ("2", "A feature flips, the score does not",
               "Cohen's d +0.80 to -0.26 while classifier AUROC moves 0.000"),
              ("3", "Complementary arms on an unseen generator",
               "pixel arm at chance, yet +0.061 AUROC [0.028, 0.094] when combined")]
    y = Inches(1.8)
    for num, title, desc in claims:
        textbox(s, M, y - Inches(0.06), Inches(0.75), Inches(0.7), num, size=34, bold=True,
                color=ACCENT, font=DISPLAY)
        textbox(s, M + Inches(0.8), y, Inches(11.3), Inches(0.4), title, size=18, bold=True,
                font=DISPLAY, color=TEXT)
        textbox(s, M + Inches(0.8), y + Inches(0.38), Inches(11.3), Inches(0.4), desc, size=13.5,
                color=MUTED)
        y += Inches(1.02)
    band = s.shapes.add_shape(1, 0, Inches(5.15), SW, Inches(1.6))
    band.fill.solid(); band.fill.fore_color.rgb = TINT; band.line.fill.background()
    textbox(s, M, Inches(5.42), Inches(12.1), Inches(1.1),
            "Umbrella claim: no retrieved abstract reports this exact protocol.\n"
            "We build on Frank '20, Dzanic '20, Durall '20, Nataraj '19, NPR '24 - we claim the "
            "measurement, not a state-of-the-art detector.",
            size=13.5, color=TEXT, spacing=1.15)
    footer(s, 4, TOTAL)
    notes(s, "Member 2, about two minutes - this is the highlighted block. Our novelty is a measurement, "
             "not a method. Claim one: we split the JPEG question into two separate verdicts per feature - "
             "does the feature value change, and does classification change - and the two come apart. "
             "Claim two, the sharpest: the Nyquist-band feature reverses its direction of separation under "
             "compression; its effect size goes from plus zero point eight to minus zero point two six, "
             "while the classifier AUROC does not move. A value-level finding invisible to detector-level "
             "studies. Claim three: on a generator the model never saw, the pixel arm is at chance alone, "
             "but adding it to the frequency arm gains six AUROC points - the arms catch different fakes. "
             "The umbrella sentence: no retrieved abstract reports this exact protocol. We say protocol, "
             "not discovery - the biases themselves were shown by Grommelt and B-Free; we provide the "
             "per-feature anatomy. Next slide shows claim two in one picture.")

    # 5 novelty evidence
    s = add_slide(prs)
    header(s, "A feature flips, the score does not", kicker="Member 2 - Novelty, the evidence")
    numeral(s, "02")
    figure(s, ext / "f11_reversal.png", M, Inches(1.62), SW - 2 * M, Inches(4.6),
           caption="f11 reverses direction for BigGAN (0.009 to 0.772) while its pooled effect size crosses zero.",
           source="Source: results/per_feature_statistics.csv and features/features.parquet - config 87f5489e9d59")
    footer(s, 5, TOTAL)
    notes(s, "Member 2 continues, thirty seconds: This picture is claims one and two at once. Left panel: "
             "for BigGAN the Nyquist-band ratio starts at zero point zero zero nine - nearly perfect "
             "separation in the reversed direction - and rises to zero point seven seven two at JPEG "
             "quality fifty, because JPEG block edges add near-Nyquist energy to images the resize had "
             "emptied. Right panel: the pooled effect size crosses zero. Meanwhile the pooled classifier "
             "AUROC moves by zero point zero zero zero. Value changed, classification did not. That is why "
             "we report the two verdicts separately.")

    # 6 methodology pipeline
    s = add_slide(prs)
    header(s, "The locked pipeline", kicker="Member 3 - Methodology / architecture")
    numeral(s, "03")
    figure(s, ROOT / "src" / "pipeline-diagram.png", M, Inches(1.62), Inches(8.3), Inches(4.6),
           caption="Stages 0-10 run in order; each stage checks its outputs and stops the study on a failed check.",
           source="Specification: src/experimental-pipeline.md, locked 2026-09-14 before any result")
    side = [("Locked before data", "config 87f5489e9d59 - one documented deviation"),
            ("Every number traceable", "hash, code version and seeds on every table"),
            ("Reproducible", "clean rerun: every table byte-for-byte")]
    cy = Inches(1.95)
    for lead, sub in side:
        textbox(s, Inches(9.25), cy, Inches(3.5), Inches(0.32), lead, size=14, bold=True, color=PRIMARY)
        textbox(s, Inches(9.25), cy + Inches(0.3), Inches(3.5), Inches(0.85), sub, size=12,
                color=MUTED, spacing=1.08)
        cy += Inches(1.32)
    footer(s, 6, TOTAL)
    notes(s, "Member 3, about one minute: The whole study runs on a pipeline that was written down and "
             "locked before we downloaded a single image. Stage zero fixes the configuration: dataset, "
             "quota, generators, features, classifier, seeds. Every stage after that checks its own outputs "
             "and stops the study if a check fails. Nothing marked LOCK was changed after results were "
             "seen; the one change we ever made - the shuffled-label control - is a dated, owner-approved "
             "deviation recorded before the rerun. On the right: every table carries the config hash and "
             "seeds, and a clean rerun reproduced every table byte for byte. Next: what goes into the "
             "comparison.")

    # 7 methodology: procedure
    s = add_slide(prs)
    header(s, "One fair procedure, four guards")
    numeral(s, "03")
    cols = [("Data and conditions",
             "3,000 parents  -  1,500 real + 1,500 fake\n\n"
             "C0   canonical 256x256 PNG\nC1   both classes JPEG q90 / 75 / 50\n"
             "C2   mismatch control only\n\n"
             "same resize and format for both classes"),
            ("Three arms, one classifier",
             "7 pixel features\n7 frequency features\ncombined = all 14\n\n"
             "one L2 logistic regression\nC and threshold from validation only"),
            ("Four control checks",
             "always-guess          0.500\nhistory-only            0.500\n"
             "shuffled labels      0.503-0.521\npre-receipt facts    1.000\n\n"
             "group splits - no parent straddles the split")]
    colw = Inches(3.85)
    for i, (title, body) in enumerate(cols):
        x = M + i * Inches(4.15)
        textbox(s, x, Inches(1.8), colw, Inches(0.4), title, size=16, bold=True, color=PRIMARY,
                font=DISPLAY)
        ln = s.shapes.add_shape(1, x, Inches(2.25), colw, Emu(9525))
        ln.fill.solid(); ln.fill.fore_color.rgb = HAIR; ln.line.fill.background()
        textbox(s, x, Inches(2.42), colw, Inches(4.2), body, size=13, color=TEXT, spacing=1.14)
    footer(s, 7, TOTAL)
    notes(s, "Member 3 continues, about one minute: Three things make the comparison fair. First, "
             "conditions: every parent exists as a canonical PNG, as both-classes JPEG at three qualities, "
             "and in a deliberate mismatch used only as a control. Second, three arms - seven pixel "
             "features, seven frequency features, and both combined - scored by the same simple logistic "
             "regression, so arm differences measure features, not classifiers. Third, four guards: a "
             "constant classifier must score one half; a history-only classifier must fail on our analysed "
             "files; shuffled labels must average one half over two hundred shuffles; and the pre-receipt "
             "facts stay visible as the known shortcut. Splits are by parent group. That is the machine. "
             "Next: the five experiments.")

    # 8 experiments
    s = add_slide(prs)
    header(s, "Five tests, one question each", kicker="Member 4 - Experiments")
    numeral(s, "04")
    textbox(s, M, Inches(1.62), Inches(12), Inches(0.3),
            "One locked test set of 600 parents is shared by all five, so every comparison across "
            "experiments is paired.", size=13.5, color=MUTED)
    exps = [("E1", "Does any arm separate the classes?", "C0, all seen"),
            ("E2", "Does a deliberate mismatch inflate scores?", "C2"),
            ("E3", "What does matched JPEG change - per feature?", "C1, q90/75/50"),
            ("E4", "Does it transfer to an unseen generator?", "C0, SD held out"),
            ("E5", "Unseen generator and JPEG together", "C1 q75, SD held out")]
    y = Inches(2.1)
    for i, (eid, q, cond) in enumerate(exps):
        textbox(s, M, y, Inches(0.8), Inches(0.4), eid, size=17, bold=True,
                color=ACCENT if eid == "E5" else PRIMARY, font=DISPLAY)
        textbox(s, M + Inches(1.0), y + Inches(0.04), Inches(8.4), Inches(0.38), q, size=15)
        textbox(s, Inches(10.2), y + Inches(0.07), Inches(2.5), Inches(0.35), cond, size=12.5,
                color=MUTED, align=PP_ALIGN.RIGHT)
        if i < 4:
            ln = s.shapes.add_shape(1, M, y + Inches(0.52), SW - 2 * M, Emu(9525))
            ln.fill.solid(); ln.fill.fore_color.rgb = HAIR; ln.line.fill.background()
        y += Inches(0.62)
    textbox(s, M, Inches(5.55), Inches(12.1), Inches(0.6),
            "Relevance: E2 rules out shortcuts  -  E3 isolates compression  -  E4 and E5 isolate "
            "generator shift.", size=14, color=TEXT)
    footer(s, 8, TOTAL)
    notes(s, "Member 4, about one minute: Five experiments, each answering one question. E1 is the first "
             "check: does any signal exist under fair conditions. E2 is a control, not a detection result: "
             "if we treat the two classes differently on purpose, a careless pipeline should light up - and "
             "we need to know how much. E3 applies matched JPEG to both classes at qualities ninety, "
             "seventy-five and fifty, and asks what changes per feature. E4 holds out an entire generator "
             "family - Stable Diffusion v1.4 - from training. E5 combines the two stresses and is our "
             "headline. One locked test set of six hundred parents is shared across all five, so every "
             "difference is paired on the same images. Next: what came out.")

    # 9 results E1 - native table + stat
    s = add_slide(prs)
    header(s, "Signal exists - and it is uneven", kicker="Member 5 - Results analysis")
    numeral(s, "05")
    tbl_shape = s.shapes.add_table(4, 4, M, Inches(1.85), Inches(7.3), Inches(2.1))
    tbl = tbl_shape.table
    widths = [Inches(2.5), Inches(1.7), Inches(1.9), Inches(1.2)]
    for i, wd in enumerate(widths):
        tbl.columns[i].width = wd
    hdr = ["Arm", "AUROC", "95% CI", "Bal. acc."]
    vals = [("Pixel-pattern", "0.666", "0.622 to 0.707", "0.612"),
            ("Frequency", "0.752", "0.713 to 0.792", "0.685"),
            ("Combined", "0.793", "0.759 to 0.826", "0.700")]
    for j, t in enumerate(hdr):
        set_cell(tbl.cell(0, j), t, size=13.5, bold=True, color=WHITE, fill=PRIMARY,
                 align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
    for i, row in enumerate(vals):
        emph = row[0] == "Combined"
        for j, t in enumerate(row):
            set_cell(tbl.cell(i + 1, j), t, size=13.5, bold=emph,
                     color=ACCENT if (emph and j == 1) else TEXT,
                     fill=TINT if emph else WHITE,
                     align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
            cell_border_bottom(tbl.cell(i + 1, j))
    textbox(s, M, Inches(4.35), Inches(7.3), Inches(1.6),
            "Per generator (combined):  BigGAN 0.990  -  SD v1.4 0.712  -  ADM 0.678\n"
            "Paired: freq beats pixel +0.087  -  combined beats freq +0.041  -  H1 supported",
            size=14, color=TEXT, spacing=1.3)
    stat(s, Inches(8.6), Inches(2.0), "0.793", "combined AUROC in the clean condition - carried\n"
         "heavily by BigGAN, which the next slide explains\n\nSource: results/family_comparison.csv",
         w=Inches(4.1), num_size=64, color=PRIMARY)
    footer(s, 9, TOTAL)
    notes(s, "Member 5, about one minute for this and the next slide: E1 says the signal exists - all "
             "three arms clear chance with room to spare, and combined wins at zero point seven nine "
             "three. But look at the per-generator rows: BigGAN is almost solved at zero point nine nine, "
             "while the two diffusion families sit at zero point six eight to zero point seven one. "
             "Whenever a pooled number hides a spread that large, ask what the pooled number is measuring. "
             "The next slide answers that.")

    # 10 results: shortcut
    s = add_slide(prs)
    header(s, "The pooled number is mostly a resize artifact")
    numeral(s, "05")
    figure(s, ext / "shortcut_anatomy.png", M, Inches(1.62), SW - 2 * M, Inches(4.6),
           caption="BigGAN's high-band features separate at 0.97+ reversed - the pipeline's own 2x resize, not the generator.",
           source="Source: features/features.parquet + data/splits.csv, recomputed in src/analysis_figures.py - config 87f5489e9d59")
    footer(s, 10, TOTAL)
    notes(s, "Member 5 continues: Here is the anatomy. Each bar is one feature's univariate AUROC for one "
             "generator. For BigGAN, every high-frequency feature separates almost perfectly - in the "
             "reversed direction, the faint dashed bars. The reason is our own locked resize: BigGAN "
             "generates at 128 pixels, the pipeline upsamples to 256 with bicubic, and that empties the top "
             "of the spectrum. The features found the resize, not the generator. The diffusion families, "
             "which were not upsampled, show nothing like it. So resizing history beat generation as a "
             "signal, and per-generator rows, not pooled rows, carry the interpretation. This is exactly "
             "the class of bias Grommelt documented - we add its per-feature anatomy.")

    # 11 results: shift
    s = add_slide(prs)
    header(s, "Generator shift is the real cost")
    numeral(s, "05")
    figure(s, ext / "degradation_path.png", M, Inches(1.7), Inches(7.7), Inches(4.55),
           caption="AUROC on SD v1.4 fakes, seen vs unseen, 95% bootstrap CIs.",
           source="Source: results/generator_shift.csv, results/family_comparison.csv, results/jpeg_robustness.csv")
    stats = [("Held-out SD v1.4 (combined)", "0.712 seen  ->  0.634 unseen  (-0.078)"),
             ("Headline E5 (unseen + q75)", "0.629  [0.571, 0.690]"),
             ("Pixel arm", "falls to chance:  0.465"),
             ("Matched JPEG on top", "only -0.004 more (refit per condition)"),
             ("Exploratory", "ADM rises +0.071 when SD leaves training")]
    cy = Inches(1.85)
    for lead, sub in stats:
        textbox(s, Inches(8.55), cy, Inches(4.2), Inches(0.3), lead, size=13.5, bold=True,
                color=ACCENT if "Headline" in lead else PRIMARY)
        textbox(s, Inches(8.55), cy + Inches(0.28), Inches(4.2), Inches(0.5), sub, size=12.5,
                color=TEXT, spacing=1.05)
        cy += Inches(0.92)
    footer(s, 11, TOTAL)
    notes(s, "Member 5 continues: E4 and E5 are the stress tests. Holding out Stable Diffusion costs the "
             "combined arm eight AUROC points. The pixel arm collapses to chance. Matched JPEG on top of "
             "shift costs almost nothing more - four thousandths - because the classifier is refit on the "
             "compressed condition, and the reals already carry JPEG history. One exploratory observation: "
             "when we removed SD from training, ADM separation went up by seven points, which suggests the "
             "two diffusion families pull the boundary in different directions. Headline, with its "
             "interval: zero point six two nine, zero point five seven one to zero point six nine zero. "
             "Modest by design - it is a measurement, not a product.")

    # 12 results: complementarity
    s = add_slide(prs)
    header(s, "At chance alone, useful in combination")
    numeral(s, "05")
    figure(s, ext / "arm_complementarity.png", M, Inches(1.85), Inches(7.9), Inches(4.4),
           caption="Unseen SD v1.4 fakes flagged at the validation threshold (E5).",
           source="Source: results/per_image_predictions.parquet, E5 rows - config 87f5489e9d59")
    textbox(s, Inches(8.85), Inches(2.1), Inches(3.9), Inches(4.0),
            "pixel flags 34 / 100\nfrequency flags 19 / 100\nunion 41  -  both missed 59\n\n"
            "combined beats frequency\n+0.061 AUROC [0.028, 0.094]\n\n"
            "the arms catch different fakes",
            size=15, color=TEXT, spacing=1.25)
    footer(s, 12, TOTAL)
    notes(s, "Member 5 finishes: Why does an arm at chance help? Because at the chosen threshold the pixel "
             "arm flags thirty-four of the hundred unseen fakes, the frequency arm nineteen, and they flag "
             "different images - the union is forty-one. In ranking terms, adding the seven pixel features "
             "to the frequency set gains six points of AUROC, interval zero point zero two eight to zero "
             "point zero nine four. Being at chance as a standalone detector does not mean carrying no "
             "information. That is the complementarity finding.")

    # 13 results: controls & verdicts
    s = add_slide(prs)
    header(s, "Why to believe the numbers: controls and verdicts")
    numeral(s, "05")
    figure(s, ext / "controls_and_verdicts.png", M, Inches(1.62), SW - 2 * M, Inches(4.6),
           caption="Only the E2 history-only check reaches 1.000 - where the mismatch is real by design.",
           source="Source: results/control_checks.csv - shuffled-label gate is the documented deviation 1 (mean of 200 shuffles)")
    footer(s, 13, TOTAL)
    notes(s, "Member 5 closes the results block, forty-five seconds: One more table before limitations - "
             "the evidence that the pipeline is sound. Left: the four control checks in every experiment. "
             "The only one allowed to reach one point zero is the history-only check in E2, where the "
             "mismatch is real by design. Right: all five pre-registered hypotheses and their verdicts, "
             "each with the number behind it: H1 supported, H2 partly, H3 supported in an unexpected form, "
             "H4 supported for SD v1.4, H5 not tested by design. The controls did most of the interpretive "
             "work in this study.")

    # 14 limitations
    s = add_slide(prs)
    header(s, "What our claims do not cover", kicker="Member 6 - Limitations")
    numeral(s, "06")
    lims = [("Scope", "three families, one dataset, one encoder, one fold"),
            ("Pooled numbers", "inflated by the BigGAN resize artifact - reported, not corrected"),
            ("Pre-receipt history", "file facts separate the dataset perfectly"),
            ("Content bias (H5)", "not tested - reals and fakes are not content-matched"),
            ("Robustness", "refit robustness only; transfer unmeasured"),
            ("Data source", "public mirror - fidelity beyond format unchecked")]
    y = Inches(1.8)
    for i, (dim, body) in enumerate(lims):
        textbox(s, M, y, Inches(2.6), Inches(0.55), dim, size=14, bold=True, color=PRIMARY)
        textbox(s, M + Inches(2.8), y, Inches(9.9), Inches(0.6), body, size=13, color=TEXT,
                spacing=1.08)
        if i < len(lims) - 1:
            ln = s.shapes.add_shape(1, M, y + Inches(0.62), SW - 2 * M, Emu(9525))
            ln.fill.solid(); ln.fill.fore_color.rgb = HAIR; ln.line.fill.background()
        y += Inches(0.8)
    footer(s, 14, TOTAL)
    notes(s, "Member 6, about two minutes: We bound our own claims before anyone else does. Scope: three "
             "generator families, one dataset, one JPEG encoder, three quality levels, one held-out fold - "
             "nothing beyond that. The pooled numbers are inflated by the resize artifact; we chose to "
             "report it rather than correct it, because correcting it would have changed a locked value. "
             "The pre-receipt facts classify this dataset perfectly, so any separation here may partly "
             "measure processing history. Content bias is untested - reals and fakes are not "
             "content-matched - and our robustness is refit robustness, not transfer of a fixed model. "
             "Finally, images came from a public mirror; we verified format and size, not pixels. These are "
             "the edges of the map. Next: what we would run next.")

    # 15 future extensions
    s = add_slide(prs)
    header(s, "Three planned next tests", kicker="Member 7 - Future extensions")
    numeral(s, "07")
    exts = [("Transfer test", "clean models scored on JPEG images, no refit"),
            ("Complete the fold rotation", "hold out ADM and BigGAN too"),
            ("Never-enlarge resize", "crop, don't upsample - does the shortcut vanish?")]
    y = Inches(1.9)
    for i, (title, desc) in enumerate(exts):
        textbox(s, M, y - Inches(0.06), Inches(0.75), Inches(0.7), str(i + 1), size=34, bold=True,
                color=PRIMARY, font=DISPLAY)
        textbox(s, M + Inches(0.8), y, Inches(11.3), Inches(0.4), title, size=18, bold=True,
                font=DISPLAY, color=TEXT)
        textbox(s, M + Inches(0.8), y + Inches(0.38), Inches(11.3), Inches(0.4), desc, size=13.5,
                color=MUTED)
        y += Inches(1.0)
    band = s.shapes.add_shape(1, 0, Inches(5.2), SW, Inches(1.45))
    band.fill.solid(); band.fill.fore_color.rgb = TINT; band.line.fill.background()
    textbox(s, M, Inches(5.48), Inches(12.1), Inches(1.0),
            "Each extension: a new pre-registered config - the locked one is never edited.\n"
            "Everything regenerates: config 87f5489e9d59  -  seeds 2026 / 20260914.",
            size=13.5, color=TEXT, spacing=1.2)
    footer(s, 15, TOTAL)
    notes(s, "Member 7, about two minutes: Three extensions, each cheap because everything is already "
             "computed. First, the transfer test: take our clean-condition models and score them on "
             "compressed images without refitting - that is the robustness people usually mean, and our "
             "saved models make it a minutes-long run. Second, complete the rotation: hold out ADM and "
             "then BigGAN, the same way we held out SD, to see whether the drop is general. Third, the "
             "sharpest one: a resize policy that never enlarges. If the BigGAN shortcut vanishes, we have "
             "proven the mechanism. All three run under a new pre-registered configuration - we do not "
             "touch the locked one. And everything you saw today regenerates from the repository: config "
             "hash, seeds, byte-identical rerun. Content matching in the TwinSynths style would address the "
             "bias we did not test. Thank you - questions welcome.")

    # 16 closing (dark)
    s = add_slide(prs)
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background()
    textbox(s, M, Inches(1.7), Inches(11.8), Inches(1.9),
            "Simple features carry real but fragile signal -\nand per-feature, per-generator reporting\nis the right unit of measurement.",
            size=28, bold=True, color=WHITE, font=DISPLAY, spacing=1.12)
    trio = [("0.629", "headline AUROC, unseen SD v1.4 at JPEG q75"),
            ("+0.061", "gain from adding the at-chance pixel arm"),
            ("1.000", "AUROC of the file-history shortcut, excluded")]
    x = M
    for num, lab in trio:
        textbox(s, x, Inches(4.35), Inches(3.9), Inches(0.75), num, size=34, bold=True,
                color=WHITE, font=DISPLAY)
        textbox(s, x, Inches(5.05), Inches(3.7), Inches(0.6), lab, size=12, color=PAPER,
                spacing=1.05)
        x += Inches(4.15)
    textbox(s, M, Inches(6.35), Inches(11.8), Inches(0.7),
            "Thank you - questions welcome.\nPre-registered study - config 87f5489e9d59 - seeds 2026 / 20260914",
            size=13, color=PAPER, spacing=1.3)
    notes(s, "Closing (member 7 or all together, fifteen seconds): One sentence to take away: simple "
             "features carry real but fragile signal, and the right way to measure them is per feature, "
             "per generator, with explicit controls. Thank you - we are happy to take questions.")

    # 17 backup
    s = add_slide(prs)
    header(s, "Backup: headline ROC and per-feature effect sizes", kicker="For questions")
    numeral(s, "B")
    figure(s, ext / "roc_headline.png", M, Inches(1.7), Inches(6.4), Inches(2.7))
    figure(s, ext / "effect_size_heatmap.png", Inches(7.3), Inches(1.7), Inches(5.4), Inches(2.7))
    textbox(s, M, Inches(4.75), Inches(12.1), Inches(1.9),
            "E5 ROC: combined 0.786 on all test generators - 0.629 on unseen SD v1.4\n"
            "Cohen's d, 14 features x 4 conditions: the f11 sign flip outlined - f14 flat at zero\n"
            "Score medians (E5 combined): real -1.36  -  BigGAN +3.83  -  SD v1.4 -0.66  -  ADM -0.16",
            size=14, color=TEXT, spacing=1.35)
    footer(s, 17, TOTAL)
    notes(s, "Backup slide for questions: ROC curves for the headline, the full effect-size heatmap, and "
             "the score medians. If asked why BigGAN carries the pooled number, point at the plus three "
             "point eight median score versus minus one point four for reals.")

    prs.save(OUT)
    print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")


if __name__ == "__main__":
    build()
