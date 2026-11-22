"""Deck: the existing deck's framing and boards, for the balustrade to bolt onto.

Run with FreeCAD's own Python (from the repo root):
    "C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe" deck/build.py

Writes out/deck.FCStd, out/deck.step and out/deck_cut_list.csv, prints the
joist layout, cut list and checks, and exits 1 if any check fails.

Coordinates match balustrade/build.py, in mm: the origin is the outside corner
where the two balustraded edges meet, the long edge runs along +X, the short
edge along +Y, and z = 0 is the deck surface. The outside faces of the edge
framing are at x = 0 and y = 0.

Joist names follow MBIE's Guidance on Barrier Design (1.2): a boundary joist
runs across the outer ends of the joists; an edge joist is the outermost joist,
parallel to the others.
"""

import csv
import math
import os
import sys

import FreeCAD as App
import Part

# --- Deck (measured or reported by Josh) -----------------------------------
LENGTH = 6000.0  # long edge, along X (about 6 m)
WIDTH = 3000.0  # short edge, along Y (about 3 m)
DECK_HEIGHT = 960.0  # deck surface above the ground at the highest point
# The joists run along the short edge (Y), 190x45. The two balustraded edges
# have doubled framing: a double boundary joist along the long edge (y = 0)
# and a double edge joist along the short edge (x = 0).
JOIST_D, JOIST_T = 190.0, 45.0  # depth, thickness
EDGE_PLIES = 2  # joists side by side on the two balustraded edges
DECKING_W, DECKING_T = 90.0, 19.0  # hardwood boards, running along X across the joists

# --- Not measured yet: placeholders ----------------------------------------
# Centre of each joist between the edge joists, as x from the corner. None
# spaces them evenly at MAX_JOIST_SPACING or less. Measure these: where the
# joist ends meet the long edge decides where the long run's bolts can go.
JOIST_CENTRES = None
MAX_JOIST_SPACING = 450.0
DECKING_GAP = 4.0  # between boards
# How far the boards run past the outside face of the framing on the two
# balustraded edges. Above 0 they would have to be notched round the posts.
DECKING_OVERHANG = 0.0

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")

JOIST_TOP = -DECKING_T
JOIST_BOTTOM = JOIST_TOP - JOIST_D
EDGE_T = EDGE_PLIES * JOIST_T  # thickness of the doubled framing on the balustraded edges


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from two corners, any order."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def joist_centres():
    """x of each joist between the double edge joist and the far edge joist."""
    if JOIST_CENTRES is not None:
        return list(JOIST_CENTRES)
    first = EDGE_T - JOIST_T / 2  # inner ply of the double edge joist
    last = LENGTH - JOIST_T / 2  # far edge joist
    bays = math.ceil((last - first) / MAX_JOIST_SPACING)
    return [first + (last - first) * i / bays for i in range(1, bays)]


def framing():
    """Joists as a list of (label, shape). The boundary joists run the full
    length; the edge joists and joists fit between them."""
    parts = []
    y_in, y_out = EDGE_T, WIDTH - JOIST_T  # between the boundary joists
    for p in range(EDGE_PLIES):
        parts.append((f"Boundary_Ply{p}", box(0, LENGTH, p * JOIST_T, (p + 1) * JOIST_T, JOIST_BOTTOM, JOIST_TOP)))
        parts.append((f"Edge_Ply{p}", box(p * JOIST_T, (p + 1) * JOIST_T, y_in, y_out, JOIST_BOTTOM, JOIST_TOP)))
    parts.append(("FarBoundary_Joist", box(0, LENGTH, y_out, WIDTH, JOIST_BOTTOM, JOIST_TOP)))
    parts.append(("FarEdge_Joist", box(LENGTH - JOIST_T, LENGTH, y_in, y_out, JOIST_BOTTOM, JOIST_TOP)))
    for i, c in enumerate(joist_centres()):
        parts.append((f"Joist{i}", box(c - JOIST_T / 2, c + JOIST_T / 2, y_in, y_out, JOIST_BOTTOM, JOIST_TOP)))
    return parts


def decking():
    """Boards along X from the long edge (y = 0) across to the far side. The
    last board is ripped to fit."""
    parts, y, i = [], -DECKING_OVERHANG, 0
    while y < WIDTH - 0.01:
        w = min(DECKING_W, WIDTH - y)
        parts.append((f"Decking{i}", box(-DECKING_OVERHANG, LENGTH, y, y + w, JOIST_TOP, 0)))
        y += w + DECKING_GAP
        i += 1
    return parts


def deck_parts():
    """All parts of the deck, as a list of (label, shape)."""
    return framing() + decking()


def checks(parts):
    """Return a list of (name, ok, detail)."""
    centres = [EDGE_T - JOIST_T / 2] + joist_centres() + [LENGTH - JOIST_T / 2]
    widest = max(b - a for a, b in zip(centres, centres[1:]))
    boards = [s for label, s in parts if label.startswith("Decking")]
    last = min(s.BoundBox.YLength for s in boards)
    return [
        ("Joist spacing", widest <= MAX_JOIST_SPACING + 0.01, f"widest {widest:.0f} mm centres, max {MAX_JOIST_SPACING:.0f}"),
        ("Decking covers the deck", abs(max(s.BoundBox.YMax for s in boards) - WIDTH) < 0.01,
         f"{len(boards)} boards, the last ripped to {last:.0f} mm"),
        ("Doubled balustrade edges", EDGE_PLIES >= 2, f"{EDGE_PLIES} x {JOIST_T:.0f} mm = {EDGE_T:.0f} mm behind the posts"),
    ]


def cut_list(parts):
    """Rows of (member, section, length, qty), grouped by member and length."""
    counts = {}
    for label, shape in parts:
        member = "Decking" if label.startswith("Decking") else "Joist"
        section = f"{DECKING_W:.0f}x{DECKING_T:.0f}" if member == "Decking" else f"{JOIST_D:.0f}x{JOIST_T:.0f}"
        bb = shape.BoundBox
        key = (member, section, round(max(bb.XLength, bb.YLength)))
        counts[key] = counts.get(key, 0) + 1
    return sorted((m, s, l, q) for (m, s, l), q in counts.items())


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    parts = deck_parts()
    doc = App.newDocument("deck")
    for label, shape in parts:
        doc.addObject("Part::Feature", label).Shape = shape
    doc.recompute()
    doc.saveAs(os.path.join(OUT_DIR, "deck.FCStd"))
    Part.export(doc.Objects, os.path.join(OUT_DIR, "deck.step"))
    App.closeDocument(doc.Name)

    rows = cut_list(parts)
    with open(os.path.join(OUT_DIR, "deck_cut_list.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["member", "section_mm", "length_mm", "qty"])
        w.writerows(rows)

    source = "measured" if JOIST_CENTRES is not None else f"placeholder, even at {MAX_JOIST_SPACING:.0f} mm max"
    print(f"Joist centres ({source}): " + ", ".join(f"{c:.0f}" for c in joist_centres()))
    print(f"== deck: {len(parts)} parts ==")
    print("Cut list:")
    for m, s, l, q in rows:
        print(f"  {q:3} x {m:8} {s:>7}  {l} mm")
    print("Checks:")
    all_ok = True
    for check, ok, detail in checks(parts):
        print(f"  {'PASS' if ok else 'FAIL'}  {check}: {detail}")
        all_ok = all_ok and ok
    if not all_ok:
        sys.stdout.flush()  # FreeCADCmd drops unflushed output on sys.exit
        sys.exit(1)


# FreeCADCmd runs a script under its file name ("build"), not "__main__".
if __name__ in ("__main__", "build"):
    main()
