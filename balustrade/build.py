"""Deck balustrade: two perpendicular runs of posts, rails and vertical palings.

Run with FreeCAD's own Python (from the repo root):
    "C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe" balustrade/build.py

Builds one model per entry in VARIANTS, each written to out/<name>.FCStd,
out/<name>.step and out/<name>_cut_list.csv. Prints the bays, and each variant's
cut list and design checks, and exits 1 if any check fails.

Coordinates, in mm: the outside corner of the deck where the two balustraded
edges meet is the origin. The long edge runs along +X, the short edge along +Y,
the deck lies in +X/+Y, and the deck surface is z = 0. Posts are bolted to the
outside face of the edge joists, so they sit just outside the deck (x < 0 or y < 0).
Each run has its own corner post, set back from the corner along its own joist,
so the two corner posts have a gap between them and the cap rails meet over it.
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

# --- Rules: NZ F4/AS1 3rd edition, amendment 2 (effective 1 January 2017) --
BARRIER_HEIGHT_MIN = 1000.0  # Table 1, housing decks: top of barrier above the deck surface
MAX_OPENING = 100.0  # 1.2.1 b): a sphere this size must not pass through any opening
BOTTOM_RAIL_TOP_MAX = 200.0  # Figure 2(a): top of the bottom rail above the deck surface

# --- Timber: actual finished sizes, mm -------------------------------------
# MBIE Guidance on Barrier Design (March 2012), 4.2.7: radiata H3.2, SG8 wet,
# palings may be SG6. 90x90 posts, 90x45 handrail and rails, 125x25 palings.
POST = 90.0  # square post
RAIL_W, RAIL_H = 45.0, 90.0  # top and bottom rails, on edge between the posts
CAP_W, CAP_T = 140.0, 45.0  # cap rail (the handrail), laid flat over the posts and top rail
PALING_W, PALING_T = 125.0, 25.0  # vertical palings nailed to one face of the rails
PALING_FACE = "inside"  # "inside": deck side, so the rails are not footholds; or "outside"

# --- Layout ---------------------------------------------------------------
# MBIE "Barrier guide and updates": 90x90 posts at 1000 mm centres maximum.
MAX_POST_SPACING = 1000.0
POST_BELOW_DECK = 220.0  # post length below the deck surface, for the joist bolts
BOTTOM_GAP = 50.0  # deck surface to underside of the bottom rail
GAP_MARGIN = 15.0  # design paling gaps this much under MAX_OPENING, for timber movement
# Each corner post's distance back from the deck corner along its own joist.
# The opening between the two corner posts is the diagonal, CORNER_OFFSET * sqrt(2).
# None: choose it so that opening equals the widest paling gap.
CORNER_OFFSET = None

# --- Corner joint of the cap rails ----------------------------------------
# "mitre": both caps run to the outside corner and meet on a 45 degree mitre.
# "block": the long cap runs through the corner, the short cap butts onto its
#          side, and a POST-sized block, RAIL_H tall, sits between the two corner
#          posts under the joint, fixed to both posts and up into both caps.
VARIANTS = {"balustrade": "mitre", "balustrade_block": "block"}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")

# Derived heights
CAP_TOP = BARRIER_HEIGHT_MIN
CAP_BOTTOM = CAP_TOP - CAP_T  # posts stop here; the cap sits on them
TOP_RAIL_BOTTOM = CAP_BOTTOM - RAIL_H
BOTTOM_RAIL_TOP = BOTTOM_GAP + RAIL_H
POST_LEN = CAP_BOTTOM + POST_BELOW_DECK

MID = -POST / 2  # cap centreline, across each run (the post line)
CAP_OUT, CAP_IN = MID - CAP_W / 2, MID + CAP_W / 2  # cap edges, across each run
# Across each run, the palings sit flush with one face of the posts and the
# rails sit behind them, so the rails' other face is inside the post line.
if PALING_T + RAIL_W > POST:
    raise ValueError("rails plus palings are deeper than the posts")
if PALING_FACE == "inside":
    PALING_C = (-PALING_T, 0.0)
    RAIL_C = (-PALING_T - RAIL_W, -PALING_T)
else:
    PALING_C = (-POST, -POST + PALING_T)
    RAIL_C = (-POST + PALING_T, -POST + PALING_T + RAIL_W)


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from two corners, any order."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def prism(points, z0, z1):
    """Vertical prism from a closed XY outline."""
    wire = Part.makePolygon([App.Vector(x, y, z0) for x, y in points + points[:1]])
    return Part.Face(wire).extrude(App.Vector(0, 0, z1 - z0))


def post_positions(run, offset):
    """Post start positions along a run: the corner post starts `offset` back
    from the deck's corner, the end post finishes flush with the run's end, the
    rest evenly between."""
    first, last = offset, run - POST
    bays = max(1, math.ceil((last - first) / MAX_POST_SPACING))
    return [first + (last - first) * i / bays for i in range(bays + 1)]


def paling_layout(clear):
    """Number of palings and the equal gap for one bay of clear width."""
    target = MAX_OPENING - GAP_MARGIN
    n = max(0, math.ceil((clear - target) / (PALING_W + target)))
    gap = (clear - n * PALING_W) / (n + 1)
    return n, gap


def widest_gap(offset):
    """Widest paling gap across both runs for a given corner offset."""
    gaps = []
    for run in (LONG_RUN, SHORT_RUN):
        posts = post_positions(run, offset)
        gaps += [paling_layout(b - a - POST)[1] for a, b in zip(posts, posts[1:])]
    return max(gaps)


def corner_offset():
    """CORNER_OFFSET, or by bisection the offset whose diagonal corner opening
    equals the widest paling gap. Moving the corner posts back shortens the
    bays, so the gaps shrink as the corner opening grows."""
    if CORNER_OFFSET is not None:
        return CORNER_OFFSET
    lo, hi = 0.0, MAX_OPENING / math.sqrt(2)
    for _ in range(60):
        mid = (lo + hi) / 2
        if mid * math.sqrt(2) < widest_gap(mid):
            lo = mid
        else:
            hi = mid
    return lo


def build_run(run, along_x, offset, joint):
    """Return (parts, bays) for one run. parts is a list of (label, shape)."""
    # Map run space (along, across) to model space. "across" runs from the
    # joist face (0) outwards (negative), so posts sit at across in [-POST, 0].
    def xy(a, c):
        return (a, c) if along_x else (c, a)

    def place(a0, a1, c0, c1, z0, z1):
        (x0, y0), (x1, y1) = xy(a0, c0), xy(a1, c1)
        return box(x0, x1, y0, y1, z0, z1)

    posts = post_positions(run, offset)
    parts, bays = [], []
    tag = "Long" if along_x else "Short"

    for i, p in enumerate(posts):
        parts.append((f"{tag}_Post{i}", place(p, p + POST, -POST, 0, -POST_BELOW_DECK, CAP_BOTTOM)))

    for b in range(len(posts) - 1):
        a0, a1 = posts[b] + POST, posts[b + 1]
        clear = a1 - a0
        parts.append((f"{tag}_TopRail{b}", place(a0, a1, *RAIL_C, TOP_RAIL_BOTTOM, CAP_BOTTOM)))
        parts.append((f"{tag}_BottomRail{b}", place(a0, a1, *RAIL_C, BOTTOM_GAP, BOTTOM_RAIL_TOP)))
        # Palings run from the underside of the bottom rail to the cap, so each
        # one laps both rails for its nails.
        n, gap = paling_layout(clear)
        for k in range(n):
            s = a0 + gap + k * (PALING_W + gap)
            parts.append((f"{tag}_Bay{b}_Paling{k}", place(s, s + PALING_W, *PALING_C, BOTTOM_GAP, CAP_BOTTOM)))
        bays.append({"run": tag, "bay": b, "clear": clear, "palings": n, "gap": gap})

    # Cap rail centred on the post line, run out over the gap to the corner.
    if joint == "mitre":
        # Both caps reach the outside corner; the mitre runs from the outside
        # corner of the caps (CAP_OUT, CAP_OUT) to the inside one (CAP_IN, CAP_IN).
        outline = [xy(CAP_OUT, CAP_OUT), xy(run, CAP_OUT), xy(run, CAP_IN), xy(CAP_IN, CAP_IN)]
        cap = prism(outline, CAP_BOTTOM, CAP_TOP)
    else:
        # The long cap runs through the corner; the short cap butts onto its side.
        start = CAP_OUT if along_x else CAP_IN
        cap = place(start, run, CAP_OUT, CAP_IN, CAP_BOTTOM, CAP_TOP)
    parts.append((f"{tag}_Cap", cap))
    return parts, bays


def corner_block(offset):
    """POST-sized block between the two corner posts, under the cap joint. It
    touches the long corner post's end face (x = offset) and the short corner
    post's end face (y = offset)."""
    return ("Corner_Block", box(offset - POST, offset, offset - POST, offset, TOP_RAIL_BOTTOM, CAP_BOTTOM))


def checks(bays, shapes):
    """Return a list of (name, ok, detail)."""
    worst_gap = max(b["gap"] for b in bays)
    spacings = [b["clear"] + POST for b in bays]
    corner_gap = shapes["Long_Post0"].distToShape(shapes["Short_Post0"])[0]
    results = [
        ("Barrier height", CAP_TOP >= BARRIER_HEIGHT_MIN, f"top {CAP_TOP:.0f} mm, need >= {BARRIER_HEIGHT_MIN:.0f}"),
        ("Paling gaps", worst_gap < MAX_OPENING, f"widest {worst_gap:.1f} mm, need < {MAX_OPENING:.0f}"),
        ("Bottom gap", BOTTOM_GAP < MAX_OPENING, f"{BOTTOM_GAP:.0f} mm, need < {MAX_OPENING:.0f}"),
        ("Bottom rail height", BOTTOM_RAIL_TOP <= BOTTOM_RAIL_TOP_MAX, f"top at {BOTTOM_RAIL_TOP:.0f} mm, max {BOTTOM_RAIL_TOP_MAX:.0f}"),
        ("Corner opening", corner_gap < MAX_OPENING, f"{corner_gap:.1f} mm between the corner posts, need < {MAX_OPENING:.0f}"),
        ("Post spacing", max(spacings) <= MAX_POST_SPACING, f"widest {max(spacings):.0f} mm centres, max {MAX_POST_SPACING:.0f}"),
        ("Caps meet at the corner", shapes["Long_Cap"].distToShape(shapes["Short_Cap"])[0] < 0.01, "long and short caps in contact"),
    ]
    if "Corner_Block" in shapes:
        block = shapes["Corner_Block"]
        touching = [n for n in ("Long_Post0", "Short_Post0", "Long_Cap", "Short_Cap") if block.distToShape(shapes[n])[0] < 0.01]
        results.append(("Corner block bears on posts and caps", len(touching) == 4, f"touches {', '.join(touching) or 'nothing'}"))
    return results


def cut_list(parts, joint):
    """Group parts by member type and length. Returns rows of (member, section, length, qty, note).
    A part's length is its longest bounding-box side, which for a mitred cap is
    the long point."""
    sections = {"Post": f"{POST:.0f}x{POST:.0f}", "TopRail": f"{RAIL_H:.0f}x{RAIL_W:.0f}",
                "BottomRail": f"{RAIL_H:.0f}x{RAIL_W:.0f}", "Paling": f"{PALING_W:.0f}x{PALING_T:.0f}",
                "Cap": f"{CAP_W:.0f}x{CAP_T:.0f}", "Block": f"{POST:.0f}x{POST:.0f}"}
    notes = {"Cap": "45 deg mitre at the corner end, length to the long point" if joint == "mitre" else "square ends",
             "Block": "post offcut"}
    counts = {}
    for label, shape in parts:
        member = next(m for m in sections if m in label.split("_")[-1])
        bb = shape.BoundBox
        length = round(max(bb.XLength, bb.YLength, bb.ZLength))
        key = (member, sections[member], length, notes.get(member, ""))
        counts[key] = counts.get(key, 0) + 1
    return sorted((m, s, l, q, n) for (m, s, l, n), q in counts.items())


def build_variant(name, joint, offset):
    """Build, save and export one variant. Returns (parts, bays)."""
    long_parts, long_bays = build_run(LONG_RUN, along_x=True, offset=offset, joint=joint)
    short_parts, short_bays = build_run(SHORT_RUN, along_x=False, offset=offset, joint=joint)
    parts = long_parts + short_parts
    if joint == "block":
        parts.append(corner_block(offset))

    doc = App.newDocument(name)
    for label, shape in parts:
        doc.addObject("Part::Feature", label).Shape = shape
    doc.recompute()
    doc.saveAs(os.path.join(OUT_DIR, f"{name}.FCStd"))
    Part.export(doc.Objects, os.path.join(OUT_DIR, f"{name}.step"))
    App.closeDocument(doc.Name)

    rows = cut_list(parts, joint)
    with open(os.path.join(OUT_DIR, f"{name}_cut_list.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["member", "section_mm", "length_mm", "qty", "note"])
        w.writerows(rows)
    return parts, long_bays + short_bays, rows


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    offset = corner_offset()
    print(f"Corner posts: {offset:.1f} mm back from the deck corner")
    all_ok, bays_printed = True, False
    for name, joint in VARIANTS.items():
        parts, bays, rows = build_variant(name, joint, offset)
        if not bays_printed:
            print("Bays:")
            for b in bays:
                print(f"  {b['run']:5} bay {b['bay']}: clear {b['clear']:.0f} mm, {b['palings']} palings, gaps {b['gap']:.1f} mm")
            bays_printed = True
        print(f"\n== {name} ({joint} corner): {len(parts)} parts ==")
        print("Cut list:")
        for m, s, l, q, n in rows:
            print(f"  {q:3} x {m:10} {s:>7}  {l} mm" + (f"  ({n})" if n else ""))
        print("Checks:")
        for check, ok, detail in checks(bays, dict(parts)):
            print(f"  {'PASS' if ok else 'FAIL'}  {check}: {detail}")
            all_ok = all_ok and ok
    if not all_ok:
        sys.stdout.flush()  # FreeCADCmd drops unflushed output on sys.exit
        sys.exit(1)


main()
