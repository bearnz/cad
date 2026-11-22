"""Deck with balustrade: the deck and balustrade models together, with the
bolts that fix each post to the deck framing.

Run with FreeCAD's own Python (from the repo root):
    "C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe" deck_with_balustrade/build.py

Builds both models from their own scripts (deck/build.py and the "balustrade"
variant of balustrade/build.py), so a change to either shows up here. Writes
out/deck_with_balustrade.FCStd, .step and _fixings.csv, prints each post's
bolt positions and the checks, and exits 1 if any check fails. A check that
depends on joist positions nobody has measured yet prints TODO, not FAIL.

Each post gets two M12 through-bolts, through the post and the doubled framing
behind it, as in MBIE's Guidance on Barrier Design (March 2012), Figure 4.8.
The nut and inside washer need room on the deck side of the framing, so each
bolt pair sits as near the middle of its post as it can while clearing the
joists and the other bolts.
"""

import csv
import importlib.util
import math
import os
import sys

import FreeCAD as App
import Part

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def load(name, path):
    """Import a design's build.py under its own name, without running its build."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bal = load("balustrade_build", "balustrade/build.py")
deck = load("deck_build", "deck/build.py")

VARIANT = "balustrade"  # which balustrade variant to fit (see bal.VARIANTS)

# --- Post fixing: MBIE Guidance on Barrier Design (March 2012), Figure 4.8 --
BOLT_D = 12.0  # 2 x M12 bolts per post
BOLT_EDGE_IN_JOIST = 25.0  # each bolt centre this far from the top or bottom of the joist
WASHER, WASHER_T = 50.0, 3.0  # 50x50x3 washers under the head and the nut; don't countersink

# --- Not from the guide: placeholders to check --------------------------------
HEAD_H, NUT_H, NUT_DIA = 7.5, 10.8, 21.0  # M12 hex head and nut, approximate, for clearances
BOLT_TAIL = 2 * 1.75  # thread left past the nut: two pitches of M12 coarse
MIN_BOLT_EDGE_IN_POST = 30.0  # closest a bolt centre may come to the side of its post
CLEARANCE = 2.0  # least gap between a bolt's inside hardware and other joists or bolts

OUT_DIR = os.path.join(ROOT, "out")
JOINT_T = deck.EDGE_T  # thickness of the doubled framing the bolts pass through
BOLT_Z = (deck.JOIST_TOP - BOLT_EDGE_IN_JOIST, deck.JOIST_BOTTOM + BOLT_EDGE_IN_JOIST)
GRIP = bal.POST + JOINT_T + 2 * WASHER_T
BOLT_LEN = math.ceil((GRIP + NUT_H + BOLT_TAIL) / 10) * 10


class Run:
    """Map run space to model space, as in balustrade/build.py: `a` along the
    run, `c` across it (c < 0 outside the framing, c > 0 towards the deck)."""

    def __init__(self, along_x):
        self.along_x = along_x
        self.tag = "Long" if along_x else "Short"
        # The plies each run's posts are bolted through
        self.plies = "Boundary_Ply" if along_x else "Edge_Ply"

    def box(self, a0, a1, c0, c1, z0, z1):
        if self.along_x:
            return bal.box(a0, a1, c0, c1, z0, z1)
        return bal.box(c0, c1, a0, a1, z0, z1)

    def cyl(self, r, a, c0, c1, z):
        base = App.Vector(a, c0, z) if self.along_x else App.Vector(c0, a, z)
        axis = App.Vector(0, 1, 0) if self.along_x else App.Vector(1, 0, 0)
        return Part.makeCylinder(r, c1 - c0, base, axis)


def inside_envelopes(run, a, z):
    """Bounding boxes of a bolt's inside washer, nut and tail, for clearances."""
    c0 = JOINT_T
    washer = run.box(a - WASHER / 2, a + WASHER / 2, c0, c0 + WASHER_T, z - WASHER / 2, z + WASHER / 2).BoundBox
    nut = run.box(a - NUT_DIA / 2, a + NUT_DIA / 2, c0 + WASHER_T, c0 + WASHER_T + NUT_H + BOLT_TAIL,
                  z - NUT_DIA / 2, z + NUT_DIA / 2).BoundBox
    return [washer, nut]


def bolt(run, a, z):
    """One bolt, head outside the post and nut on the deck side, as one solid."""
    out, ins = -bal.POST, JOINT_T
    pieces = [
        run.cyl(NUT_DIA / 2, a, out - WASHER_T - HEAD_H, out - WASHER_T, z),  # head
        run.box(a - WASHER / 2, a + WASHER / 2, out - WASHER_T, out, z - WASHER / 2, z + WASHER / 2),
        run.box(a - WASHER / 2, a + WASHER / 2, ins, ins + WASHER_T, z - WASHER / 2, z + WASHER / 2),
        run.cyl(NUT_DIA / 2, a, ins + WASHER_T, ins + WASHER_T + NUT_H, z),  # nut
    ]
    shank = run.cyl(BOLT_D / 2, a, out - WASHER_T, ins + WASHER_T + NUT_H + BOLT_TAIL, z)
    return shank.fuse(pieces).removeSplitter()


def gap(b1, b2):
    """Gap between two bounding boxes: positive if apart, 0 touching, negative overlapping."""
    return max(b2.XMin - b1.XMax, b1.XMin - b2.XMax, b2.YMin - b1.YMax, b1.YMin - b2.YMax,
               b2.ZMin - b1.ZMax, b1.ZMin - b2.ZMax)


def clear(envelopes, framing, boards, placed):
    """Names of what the envelopes hit: framing and bolts within CLEARANCE, or
    an overlapped decking board (the washers can touch the boards' underside)."""
    hits = []
    for label, bb in framing:
        if any(gap(e, bb) < CLEARANCE - 1e-6 for e in envelopes):
            hits.append(label)
    for label, bb in boards:
        if any(gap(e, bb) < -1e-6 for e in envelopes):
            hits.append(label)
    for label, bb in placed:
        if any(gap(e, bb) < CLEARANCE - 1e-6 for e in envelopes):
            hits.append(label)
    return hits


def place_bolts(run, post, deck_bbs, placed):
    """Choose where along the post its bolt pair goes. Returns (a, blocked_by):
    the position nearest the post's centre whose inside hardware clears
    everything, or, failing that, the nearest that clears all but the joists
    between the edge joists, with the joists it hits. a is None if even that
    fails."""
    bb = post.BoundBox
    p0 = bb.XMin if run.along_x else bb.YMin
    centre = p0 + bal.POST / 2
    reach = bal.POST / 2 - MIN_BOLT_EDGE_IN_POST
    candidates = sorted((centre + d / 2 for d in range(-int(2 * reach), int(2 * reach) + 1)),
                        key=lambda a: abs(a - centre))
    framing = [(l, b) for l, b in deck_bbs if not l.startswith(("Decking", run.plies))]
    boards = [(l, b) for l, b in deck_bbs if l.startswith("Decking")]

    def hits(a):
        return [h for z in BOLT_Z for h in clear(inside_envelopes(run, a, z), framing, boards, placed)]

    for a in candidates:
        if not hits(a):
            return a, []
    for a in candidates:
        blocked = hits(a)
        if all(h.startswith("Joist") for h in blocked):
            return a, sorted(set(blocked))
    return None, []


def overlaps(parts, allowed):
    """Pairs of parts that overlap by more than 1 mm^3, except allowed pairs."""
    found = []
    for i, (la, sa) in enumerate(parts):
        for lb, sb in parts[i + 1:]:
            if {la, lb} in allowed or gap(sa.BoundBox, sb.BoundBox) >= 0:
                continue
            v = sa.common(sb).Volume
            if v > 1.0:
                found.append(f"{la}/{lb} {v:.0f} mm3")
    return found


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    joint, block = bal.VARIANTS[VARIANT]
    bal_parts, _ = bal.design_parts(joint, block)
    deck_parts = deck.deck_parts()
    deck_bbs = [(l, s.BoundBox) for l, s in deck_parts]
    measured = deck.JOIST_CENTRES is not None

    # Bolt the posts: the long run first, then the short run, so each bolt
    # pair clears the ones already placed (they meet at the corner).
    shapes = dict(bal_parts + deck_parts)
    fixings, bolts, holes, placed, allowed = [], [], {}, [], []
    for run in (Run(True), Run(False)):
        posts = sorted((l for l, _ in bal_parts if l.startswith(f"{run.tag}_Post")), key=lambda l: int(l[len(run.tag) + 5:]))
        for label in posts:
            post = shapes[label]
            a, blocked = place_bolts(run, post, deck_bbs, placed)
            bb = post.BoundBox
            centre = (bb.XMin if run.along_x else bb.YMin) + bal.POST / 2
            fixings.append({"post": label, "a": a, "offset": None if a is None else a - centre, "blocked": blocked})
            if a is None:
                continue
            for name, z in zip(("Upper", "Lower"), BOLT_Z):
                bl = f"{label}_Bolt{name}"
                bolts.append((bl, bolt(run, a, z)))
                placed += [(bl, e) for e in inside_envelopes(run, a, z)]
                allowed += [{bl, j} for j in blocked]
                hole = run.cyl(BOLT_D / 2, a, -bal.POST, JOINT_T, z)
                for target in [label] + [l for l, _ in deck_parts if l.startswith(run.plies)]:
                    holes.setdefault(target, []).append(hole)

    # Drill the posts and plies for the bolts
    for target, hs in holes.items():
        shapes[target] = shapes[target].cut(hs)
    parts = [(l, shapes[l]) for l, _ in deck_parts + bal_parts] + bolts

    doc = App.newDocument("deck_with_balustrade")
    for label, shape in parts:
        doc.addObject("Part::Feature", label).Shape = shape
    doc.recompute()
    doc.saveAs(os.path.join(OUT_DIR, "deck_with_balustrade.FCStd"))
    Part.export(doc.Objects, os.path.join(OUT_DIR, "deck_with_balustrade.step"))
    App.closeDocument(doc.Name)

    with open(os.path.join(OUT_DIR, "deck_with_balustrade_fixings.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["post", "bolt_centre_along_run_mm", "off_post_centre_mm", "bolt_heights_mm", "blocked_by"])
        for fx in fixings:
            w.writerow([fx["post"], "" if fx["a"] is None else f"{fx['a']:.0f}",
                        "" if fx["offset"] is None else f"{fx['offset']:+.0f}",
                        " / ".join(f"{z:.0f}" for z in BOLT_Z), " ".join(fx["blocked"])])

    print(f"Joist centres: {'measured' if measured else 'PLACEHOLDER, not measured'}")
    print(f"Bolts: {2 * len([f for f in fixings if f['a'] is not None])} x M12 x {BOLT_LEN} "
          f"(grip {GRIP:.0f} mm: {bal.POST:.0f} post + {JOINT_T:.0f} framing + 2 washers), "
          f"at {BOLT_Z[0]:.0f} and {BOLT_Z[1]:.0f} mm below the deck surface")
    print("Post fixings (bolt centre along the run, and off the post's centre):")
    for fx in fixings:
        if fx["a"] is None:
            print(f"  {fx['post']:12} no position clears the framing")
            continue
        note = f"  blocked by {', '.join(fx['blocked'])}" if fx["blocked"] else ""
        print(f"  {fx['post']:12} {fx['a']:7.0f} mm  ({fx['offset']:+.0f}){note}")

    posts = [shapes[f["post"]] for f in fixings]
    blocked = [f["post"] for f in fixings if f["blocked"]]
    unplaced = [f["post"] for f in fixings if f["a"] is None]
    clashes = overlaps(parts, allowed)
    results = [
        ("Runs fit the deck", bal.LONG_RUN <= deck.LENGTH and bal.SHORT_RUN <= deck.WIDTH,
         f"long {bal.LONG_RUN:.0f} of {deck.LENGTH:.0f} mm, short {bal.SHORT_RUN:.0f} of {deck.WIDTH:.0f} mm"),
        ("Posts flush with the joist bottom", all(abs(p.BoundBox.ZMin - deck.JOIST_BOTTOM) < 0.01 for p in posts),
         f"post bottoms at {deck.JOIST_BOTTOM:.0f} mm (MBIE Figure 4.8)"),
        ("Posts bear on the doubled framing",
         all(shapes[f["post"]].distToShape(shapes[("Boundary" if f["post"].startswith("Long") else "Edge") + "_Ply0"])[0] < 0.01
             for f in fixings), f"{len(posts)} posts against the outside ply"),
        ("Every post has a bolt position", not unplaced, ", ".join(unplaced) or f"{len(fixings)} posts"),
        ("Bolts clear the joists", "TODO" if blocked and not measured else not blocked,
         (f"{len(blocked)} posts have a joist end behind every bolt position: {', '.join(blocked)}" if blocked
          else "every nut and washer clears the joists by at least "
          f"{CLEARANCE:.0f} mm") + ("" if measured else " (joist positions are placeholders)")),
        ("Nothing else clashes", not clashes, "; ".join(clashes[:5]) or f"{len(parts)} parts, no overlaps"),
    ]
    print("Checks:")
    failed = False
    for check, ok, detail in results:
        status = ok if ok == "TODO" else ("PASS" if ok else "FAIL")
        print(f"  {status:4}  {check}: {detail}")
        failed = failed or status == "FAIL"
    if failed:
        sys.stdout.flush()  # FreeCADCmd drops unflushed output on sys.exit
        sys.exit(1)


# FreeCADCmd runs a script under its file name ("build"), not "__main__".
if __name__ in ("__main__", "build"):
    main()
