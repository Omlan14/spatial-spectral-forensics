#!/usr/bin/env python3
"""
Pipeline diagram for the AI-generated image detection study (Figure 1).

Generates the figure as vector PDF + high-resolution PNG, sized to fit on one
page of a standard report with generous margins (6.6 x 9.3 inches fits A4 with
about 0.8-inch margins and Letter with about 0.85-inch margins; Word or LaTeX
will scale it by a few percent at worst, which is not visible). Deterministic:
rerunning
reproduces identical output.

The flow content mirrors `experimental-pipeline.md`, Section 4. If the
specification changes, update the labels below and rerun this script.

Self-checks before saving (the script exits nonzero on any failure):
  1. every text element fits inside its box (with a margin)
  2. no two text elements overlap
  3. every text element sits inside the canvas
  4. no em dash or en dash characters anywhere in the figure
"""

import sys
from dataclasses import dataclass, field

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---------------------------------------------------------------- palette
# One hue per band; accents for JPEG (C1) and the control (C2). Colour is
# never the only signal: every box carries a text label.
C_DATA = ("#E8EEF7", "#3F639B")
C_PREP = ("#E3F0EC", "#2A7361")
C_JPEG = ("#FBEEDC", "#A96C12")
C_CTRL = ("#F2F2F2", "#777777")
C_FEAT = ("#EAE6F5", "#554796")
C_EVAL = ("#E6EFE2", "#44703C")
ARROW = "#333333"
TEXT_DARK = "#141414"

TITLE = "Pipeline overview"

# ---------------------------------------------------------------- geometry
# Canvas 6.6 x 9.3 inches: fits a standard report page with room to spare,
# with clear white padding on all four sides of the content.
FIG_W, FIG_H = 6.6, 9.3
X0, X1 = 4.5, 96.5               # content column (~0.30 in padding each side)
FULL_W = X1 - X0
TRIO_GAP = 1.8                   # narrow gap between the three columns
TRIO_W = (FULL_W - 2 * TRIO_GAP) / 3.0
TRIO_X = [X0, X0 + TRIO_W + TRIO_GAP, X0 + 2 * (TRIO_W + TRIO_GAP)]
CX = (X0 + X1) / 2.0
YLIM = (-21.0, 206.0)            # ~0.28 in padding bottom, ~0.45 in top
RAIL1, RAIL2, RAIL3, RAIL4 = 117.5, 97.0, 78.6, 60.5
RAIL5, RAIL6 = 38.5, 17.5        # above and below the five experiment boxes


@dataclass
class Box:
    y: float                    # center
    h: float
    title: str
    sub: str = ""
    x: float = X0
    w: float = FULL_W
    color: tuple = C_DATA
    dashed: bool = False
    title_fs: float = 10.5
    sub_fs: float = 9.0
    texts: list = field(default_factory=list)   # filled at draw time


def draw_box(ax, b: Box):
    fill, edge = b.color
    patch = FancyBboxPatch(
        (b.x, b.y - b.h / 2), b.w, b.h,
        boxstyle="round,pad=0.15,rounding_size=2.0", mutation_aspect=1.3,
        linewidth=1.4, edgecolor=edge, facecolor=fill,
        linestyle=(0, (4, 2.5)) if b.dashed else "solid",
        zorder=2,
    )
    ax.add_patch(patch)

    n_sub_lines = (b.sub.count("\n") + 1) if b.sub else 0
    if n_sub_lines == 1:
        title_y, sub_y = b.y + b.h * 0.23, b.y - b.h * 0.19
    elif n_sub_lines == 2:
        title_y, sub_y = b.y + b.h * 0.31, b.y - b.h * 0.15
    else:
        title_y, sub_y = b.y, None

    x_center = b.x + b.w / 2.0
    t1 = ax.text(x_center, title_y, b.title, ha="center", va="center",
                 fontsize=b.title_fs, fontweight="bold", color=TEXT_DARK,
                 zorder=3)
    b.texts.append(t1)
    if sub_y is not None:
        t2 = ax.text(x_center, sub_y, b.sub, ha="center", va="center",
                     fontsize=b.sub_fs, color="#3A3A3A", zorder=3,
                     linespacing=1.55)
        b.texts.append(t2)


def v_arrow(ax, x, y_from, y_to):
    """Vertical arrow with a clearly visible head."""
    ax.add_patch(FancyArrowPatch(
        (x, y_from), (x, y_to), arrowstyle="-|>", mutation_scale=15,
        linewidth=1.8, color=ARROW, shrinkA=0, shrinkB=0, zorder=1,
        joinstyle="miter"))


def fan_out(ax, x_parent_c, y_from, y_rail, targets):
    """One box to three: down-stub, horizontal rail, one arrow per target."""
    ax.plot([x_parent_c, x_parent_c], [y_from, y_rail],
            color=ARROW, lw=1.8, zorder=1, solid_capstyle="butt")
    xs = [t[0] for t in targets]
    ax.plot([min(xs + [x_parent_c]), max(xs + [x_parent_c])],
            [y_rail, y_rail], color=ARROW, lw=1.8, zorder=1,
            solid_capstyle="butt")
    for tx, ty_top in targets:
        v_arrow(ax, tx, y_rail, ty_top)


def fan_in(ax, sources, y_rail, y_to, x_parent_c):
    """Three or more boxes to one: stubs, rail, then one arrow."""
    for sx, sy_bot in sources:
        ax.plot([sx, sx], [sy_bot, y_rail], color=ARROW, lw=1.8, zorder=1,
                solid_capstyle="butt")
    xs = [s[0] for s in sources]
    ax.plot([min(xs), max(xs)], [y_rail, y_rail], color=ARROW, lw=1.8,
            zorder=1, solid_capstyle="butt")
    v_arrow(ax, x_parent_c, y_rail, y_to)


def main():
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    ax.set_xlim(0, 100)
    ax.set_ylim(*YLIM)
    ax.axis("off")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)

    title_artist = ax.text(50, 192.5, TITLE, ha="center", va="center",
                           fontsize=13.0, fontweight="bold",
                           color=TEXT_DARK)

    boxes = []

    # ================= Data =================
    b_a1 = Box(y=180.0, h=9.5, title="Download images",
               sub="GenImage dataset: 1,500 real + 1,500 generated images",
               color=C_DATA)
    b_a2 = Box(y=163.0, h=9.5, title="Check sources and copies",
               sub="remove duplicates and near-copies of the same picture",
               color=C_DATA)
    b_a3 = Box(y=146.0, h=9.5, title="Split by image group, then lock it",
               sub="one generator kept out for testing (unseen)",
               color=C_DATA)
    boxes += [b_a1, b_a2, b_a3]

    # ================= Features =================
    b_p1 = Box(y=127.0, h=10.5,
               title="Standard pre-processing: same for both classes",
               sub="256 x 256 pixels, PNG format",
               color=C_PREP)
    boxes.append(b_p1)

    y_c, h_c = 107.0, 12.5
    c0 = Box(y=y_c, h=h_c, title="C0: standard image",
             sub="no extra compression", x=TRIO_X[0], w=TRIO_W,
             color=C_PREP, title_fs=9.8, sub_fs=8.6)
    c1 = Box(y=y_c, h=h_c, title="C1: JPEG versions",
             sub="quality 90 / 75 / 50", x=TRIO_X[1], w=TRIO_W,
             color=C_JPEG, title_fs=9.8, sub_fs=8.6)
    c2 = Box(y=y_c, h=h_c, title="C2: mismatch control",
             sub="deliberate, control only", x=TRIO_X[2], w=TRIO_W,
             color=C_CTRL, dashed=True, title_fs=9.8, sub_fs=8.6)
    boxes += [c0, c1, c2]

    b_f = Box(y=88.0, h=10.5, title="14 simple image statistics",
              sub="7 pixel-pattern features + 7 frequency features",
              color=C_FEAT)
    boxes.append(b_f)

    y_arm, h_arm = 69.5, 10.0
    a_sp = Box(y=y_arm, h=h_arm, title="Pixel-pattern", sub="7 features",
               x=TRIO_X[0], w=TRIO_W, color=C_FEAT, title_fs=9.8,
               sub_fs=8.6)
    a_fr = Box(y=y_arm, h=h_arm, title="Frequency", sub="7 features",
               x=TRIO_X[1], w=TRIO_W, color=C_FEAT, title_fs=9.8,
               sub_fs=8.6)
    a_cb = Box(y=y_arm, h=h_arm, title="Both combined", sub="14 features",
               x=TRIO_X[2], w=TRIO_W, color=C_FEAT, title_fs=9.8,
               sub_fs=8.6)
    boxes += [a_sp, a_fr, a_cb]

    # ================= Classifier & checks =================
    b_pr = Box(y=49.0, h=15.0,
               title="Train one simple classifier (logistic regression)",
               sub="settings chosen on validation data only\n"
                   "control checks: majority guess, file history only, "
                   "shuffled labels",
               color=C_JPEG)
    boxes.append(b_pr)

    # ========= Experiments: five separate boxes in one row =========
    n_exp = 5
    chip_gap = 1.6
    chip_w = (FULL_W - (n_exp - 1) * chip_gap) / n_exp
    chip_x = [X0 + i * (chip_w + chip_gap) for i in range(n_exp)]
    y_e, h_e = 29.0, 11.5
    chip_color = C_EVAL               # match the Statistics and conclusion boxes
    exp_labels = [
        "E1|can it work",
        "E2|shortcut check",
        "E3|JPEG test",
        "E4|new generator",
        "E5|both at once",
    ]
    chips = []
    for i, lab in enumerate(exp_labels):
        title, name = lab.split("|")
        chips.append(Box(y=y_e, h=h_e, title=title, sub=name,
                         x=chip_x[i], w=chip_w, color=chip_color,
                         title_fs=9.5, sub_fs=8.5))
    boxes += chips
    exp_cx = [x + chip_w / 2.0 for x in chip_x]

    # ================= Results =================
    b_s = Box(y=7.5, h=10.5, title="Statistics",
              sub="AUROC and confidence intervals from group-based resampling",
              color=C_EVAL)
    b_c = Box(y=-9.5, h=10.0, title="Careful conclusion",
              sub="we claim only what the tests support",
              color=C_EVAL)
    boxes += [b_s, b_c]

    for b in boxes:
        draw_box(ax, b)

    # ---- arrows ----------------------------------------------------------
    v_arrow(ax, CX, b_a1.y - b_a1.h / 2, b_a2.y + b_a2.h / 2)
    v_arrow(ax, CX, b_a2.y - b_a2.h / 2, b_a3.y + b_a3.h / 2)
    v_arrow(ax, CX, b_a3.y - b_a3.h / 2, b_p1.y + b_p1.h / 2)

    trio_cx = [b.x + b.w / 2 for b in (c0, c1, c2)]
    fan_out(ax, CX, b_p1.y - b_p1.h / 2, RAIL1,
            [(cx, y_c + h_c / 2) for cx in trio_cx])
    fan_in(ax, [(cx, y_c - h_c / 2) for cx in trio_cx],
           RAIL2, b_f.y + b_f.h / 2, CX)
    fan_out(ax, CX, b_f.y - b_f.h / 2, RAIL3,
            [(cx, y_arm + h_arm / 2) for cx in trio_cx])
    fan_in(ax, [(cx, y_arm - h_arm / 2) for cx in trio_cx],
           RAIL4, b_pr.y + b_pr.h / 2, CX)

    # classifier -> the five experiment boxes (fan out); the five boxes ->
    # Statistics (fan in)
    fan_out(ax, CX, b_pr.y - b_pr.h / 2, RAIL5,
            [(cx, y_e + h_e / 2) for cx in exp_cx])
    fan_in(ax, [(cx, y_e - h_e / 2) for cx in exp_cx],
           RAIL6, b_s.y + b_s.h / 2, CX)

    v_arrow(ax, CX, b_s.y - b_s.h / 2, b_c.y + b_c.h / 2)

    # ---- small label on the first fan, so the pre-processing box clearly
    #      reads as producing the three condition boxes below it
    ax.text((trio_cx[0] + trio_cx[1]) / 2, RAIL1, "three test conditions",
            ha="center", va="center", fontsize=8.5, color="#444444",
            zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.6))

    # ---- self-checks ------------------------------------------------------
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    problems = []

    for b in boxes:
        box_px = ax.transData.transform_bbox(
            matplotlib.transforms.Bbox.from_extents(
                b.x, b.y - b.h / 2, b.x + b.w, b.y + b.h / 2))
        for t in b.texts:
            ext = t.get_window_extent(renderer)
            if (ext.x0 < box_px.x0 + 2 or ext.x1 > box_px.x1 - 2
                    or ext.y0 < box_px.y0 + 2 or ext.y1 > box_px.y1 - 2):
                problems.append(
                    f"TEXT OUTSIDE BOX: '{t.get_text()[:40]}' "
                    f"ext=({ext.x0:.0f},{ext.y0:.0f},{ext.x1:.0f},{ext.y1:.0f}) "
                    f"box=({box_px.x0:.0f},{box_px.y0:.0f},"
                    f"{box_px.x1:.0f},{box_px.y1:.0f})")

    all_texts = []
    for t in [t for b in boxes for t in b.texts] + [title_artist] \
            + list(ax.texts):
        if t not in all_texts:
            all_texts.append(t)
    for i in range(len(all_texts)):
        for j in range(i + 1, len(all_texts)):
            e1 = all_texts[i].get_window_extent(renderer)
            e2 = all_texts[j].get_window_extent(renderer)
            if e1.overlaps(e2):
                problems.append(
                    f"TEXT OVERLAP: '{all_texts[i].get_text()[:30]}' vs "
                    f"'{all_texts[j].get_text()[:30]}'")

    fig_w, fig_h = fig.get_size_inches() * fig.dpi
    for t in all_texts:
        ext = t.get_window_extent(renderer)
        if (ext.x0 < 3 or ext.y0 < 3
                or ext.x1 > fig_w - 3 or ext.y1 > fig_h - 3):
            problems.append(
                f"TEXT OUTSIDE CANVAS: '{t.get_text()[:40]}' "
                f"ext=({ext.x0:.0f},{ext.y0:.0f},{ext.x1:.0f},{ext.y1:.0f}) "
                f"canvas=({fig_w:.0f}x{fig_h:.0f})")

    for t in all_texts:
        if "\u2014" in t.get_text() or "\u2013" in t.get_text():
            problems.append(
                f"DASH CHARACTER IN LABEL: '{t.get_text()[:40]}'")

    if problems:
        print("SELF-CHECK FAILED:")
        for p in problems:
            print("  " + p)
        sys.exit(1)

    print(f"Self-check passed: {len(boxes)} boxes, {len(all_texts)} text "
          f"elements, no overlaps, all texts fit, no dash characters.")
    print(f"Figure size: {FIG_W} x {FIG_H} inches "
          f"(fits one A4/Letter page with wide margins).")

    fig.savefig("pipeline-diagram.png", dpi=400, facecolor="white")
    fig.savefig("pipeline-diagram.pdf", facecolor="white")
    print("Wrote pipeline-diagram.png (400 dpi) and pipeline-diagram.pdf")


if __name__ == "__main__":
    main()
