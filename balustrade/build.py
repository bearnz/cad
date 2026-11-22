"""Deck balustrade: two perpendicular runs of posts, rails and vertical balusters.

Run with FreeCAD's own Python (from the repo root):
    "C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe" balustrade/build.py

Writes out/balustrade.FCStd, out/balustrade.step and out/balustrade_cut_list.csv,
prints the design checks and the cut list, and exits 1 if a check fails.

Coordinates, in mm: the outside corner of the deck where the two balustraded
edges meet is the origin. The long edge runs along +X, the short edge along +Y,
the deck lies in +X/+Y, and the deck surface is z = 0. Posts are bolted to the
outside face of the edge joists, so they sit just outside the deck (x < 0 or y < 0).
"""

import csv
import math
import os
import sys

import FreeCAD as App
import Part

# --- Deck (measured) -------------------------------------------------------
LONG_RUN = 5200.0  # balustrade length along the long edge, from the corner
SHORT_RUN = 1800.0  # balustrade length along the short edge, from the corner to the steps
DECK_HEIGHT = 960.0  # deck surface above ground at the highest point

# --- Rules (NZ F4 for housing). NOT YET CONFIRMED against F4/AS1: see README.
BARRIER_HEIGHT_MIN = 1000.0  # top of barrier above the deck surface
MAX_OPENING = 100.0  # a sphere this size must not pass through any gap
FOOTHOLD_ZONE = (150.0, 760.0)  # no horizontal climbable member with its top in this band

# --- Timber (finished sizes, mm). Assumed, not chosen yet. -----------------
POST = 90.0  # square post
RAIL_W, RAIL_H = 45.0, 90.0  # top and bottom rails, on edge
CAP_W, CAP_T = 140.0, 45.0  # cap rail, laid flat over posts and top rail
BALUSTER = 42.0  # square baluster

# --- Layout ---------------------------------------------------------------
MAX_POST_SPACING = 1500.0  # centre to centre. Unchecked structurally (B1).
POST_BELOW_DECK = 220.0  # post length below the deck surface, for the joist bolts
BOTTOM_GAP = 50.0  # deck surface to underside of the bottom rail
GAP_MARGIN = 5.0  # design baluster gaps this much under MAX_OPENING

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")

# Derived heights
CAP_TOP = BARRIER_HEIGHT_MIN
CAP_BOTTOM = CAP_TOP - CAP_T  # posts stop here; the cap sits on them
TOP_RAIL_BOTTOM = CAP_BOTTOM - RAIL_H
BOTTOM_RAIL_TOP = BOTTOM_GAP + RAIL_H
BALUSTER_LEN = TOP_RAIL_BOTTOM - BOTTOM_RAIL_TOP
POST_LEN = CAP_BOTTOM + POST_BELOW_DECK


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from two corners, any order."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def post_positions(run):
    """Post start positions along a run: the corner post sits at [-POST, 0],
    the end post finishes flush with the run's end, the rest evenly between."""
    first, last = -POST, run - POST
    bays = max(1, math.ceil((last - first) / MAX_POST_SPACING))
    return [first + (last - first) * i / bays for i in range(bays + 1)]


def baluster_layout(clear):
    """Number of balusters and the equal gap for one bay of clear width."""
    target = MAX_OPENING - GAP_MARGIN
    n = max(0, math.ceil((clear - target) / (BALUSTER + target)))
    gap = (clear - n * BALUSTER) / (n + 1)
    return n, gap


def build_run(run, along_x):
    """Return (parts, bays) for one run. parts is a list of (label, shape)."""
    # Map (along, across, z) in run space to model space. "across" runs from
    # the joist face (0) outwards (negative), so posts sit at across in [-POST, 0].
    def place(a0, a1, c0, c1, z0, z1):
        if along_x:
            return box(a0, a1, c0, c1, z0, z1)
        return box(c0, c1, a0, a1, z0, z1)

    mid = -POST / 2  # rail and baluster centreline, across the run
    posts = post_positions(run)
    parts, bays = [], []
    tag = "Long" if along_x else "Short"

    # The corner post belongs to the long run only, so it isn't built twice.
    for i, p in enumerate(posts):
        if i == 0 and not along_x:
            continue
        parts.append((f"{tag}_Post{i}", place(p, p + POST, -POST, 0, -POST_BELOW_DECK, CAP_BOTTOM)))

    for b in range(len(posts) - 1):
        a0, a1 = posts[b] + POST, posts[b + 1]
        clear = a1 - a0
        parts.append((f"{tag}_TopRail{b}", place(a0, a1, mid - RAIL_W / 2, mid + RAIL_W / 2, TOP_RAIL_BOTTOM, CAP_BOTTOM)))
        parts.append((f"{tag}_BottomRail{b}", place(a0, a1, mid - RAIL_W / 2, mid + RAIL_W / 2, BOTTOM_GAP, BOTTOM_RAIL_TOP)))
        n, gap = baluster_layout(clear)
        for k in range(n):
            s = a0 + gap + k * (BALUSTER + gap)
            parts.append((f"{tag}_Bay{b}_Baluster{k}", place(s, s + BALUSTER, mid - BALUSTER / 2, mid + BALUSTER / 2, BOTTOM_RAIL_TOP, TOP_RAIL_BOTTOM)))
        bays.append({"run": tag, "bay": b, "clear": clear, "balusters": n, "gap": gap})

    # Cap rail centred on the post line. The long cap runs through the corner;
    # the short cap butts against its side.
    c0 = mid - CAP_W / 2
    start = mid - CAP_W / 2 if along_x else mid + CAP_W / 2
    parts.append((f"{tag}_Cap", place(start, run, c0, c0 + CAP_W, CAP_BOTTOM, CAP_TOP)))
    return parts, bays


def checks(bays):
    """Return a list of (name, ok, detail)."""
    worst_gap = max(b["gap"] for b in bays)
    spacings = [b["clear"] + POST for b in bays]
    return [
        ("Barrier height", CAP_TOP >= BARRIER_HEIGHT_MIN, f"top {CAP_TOP:.0f} mm, need >= {BARRIER_HEIGHT_MIN:.0f}"),
        ("Baluster gaps", worst_gap < MAX_OPENING, f"widest {worst_gap:.1f} mm, need < {MAX_OPENING:.0f}"),
        ("Bottom gap", BOTTOM_GAP < MAX_OPENING, f"{BOTTOM_GAP:.0f} mm, need < {MAX_OPENING:.0f}"),
        ("Bottom rail below foothold zone", BOTTOM_RAIL_TOP <= FOOTHOLD_ZONE[0], f"top at {BOTTOM_RAIL_TOP:.0f} mm, zone starts {FOOTHOLD_ZONE[0]:.0f}"),
        ("Top rail above foothold zone", TOP_RAIL_BOTTOM >= FOOTHOLD_ZONE[1], f"underside at {TOP_RAIL_BOTTOM:.0f} mm, zone ends {FOOTHOLD_ZONE[1]:.0f}"),
        ("Post spacing", max(spacings) <= MAX_POST_SPACING, f"widest {max(spacings):.0f} mm centres, max {MAX_POST_SPACING:.0f}"),
    ]


def cut_list(parts):
    """Group parts by member type and length. Returns rows of (member, section, length, qty)."""
    sections = {"Post": f"{POST:.0f}x{POST:.0f}", "TopRail": f"{RAIL_H:.0f}x{RAIL_W:.0f}",
                "BottomRail": f"{RAIL_H:.0f}x{RAIL_W:.0f}", "Baluster": f"{BALUSTER:.0f}x{BALUSTER:.0f}",
                "Cap": f"{CAP_W:.0f}x{CAP_T:.0f}"}
    counts = {}
    for label, shape in parts:
        member = next(m for m in sections if m in label.split("_")[-1])
        bb = shape.BoundBox
        length = round(max(bb.XLength, bb.YLength, bb.ZLength))
        key = (member, sections[member], length)
        counts[key] = counts.get(key, 0) + 1
    return sorted((m, s, l, q) for (m, s, l), q in counts.items())


def main():
    long_parts, long_bays = build_run(LONG_RUN, along_x=True)
    short_parts, short_bays = build_run(SHORT_RUN, along_x=False)
    parts = long_parts + short_parts
    bays = long_bays + short_bays

    os.makedirs(OUT_DIR, exist_ok=True)
    doc = App.newDocument("Balustrade")
    for label, shape in parts:
        doc.addObject("Part::Feature", label).Shape = shape
    doc.recompute()
    doc.saveAs(os.path.join(OUT_DIR, "balustrade.FCStd"))
    Part.export(doc.Objects, os.path.join(OUT_DIR, "balustrade.step"))

    rows = cut_list(parts)
    with open(os.path.join(OUT_DIR, "balustrade_cut_list.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["member", "section_mm", "length_mm", "qty"])
        w.writerows(rows)

    print("Bays:")
    for b in bays:
        print(f"  {b['run']:5} bay {b['bay']}: clear {b['clear']:.0f} mm, {b['balusters']} balusters, gaps {b['gap']:.1f} mm")
    print("Cut list:")
    for m, s, l, q in rows:
        print(f"  {q:3} x {m:10} {s:>7}  {l} mm")
    print("Checks:")
    results = checks(bays)
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not all(ok for _, ok, _ in results):
        sys.exit(1)


main()
