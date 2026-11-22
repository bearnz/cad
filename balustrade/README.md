# Deck balustrade

Timber balustrade along two edges of the deck (about 6 m x 3 m). The two runs
meet at a right-angled outside corner:

- **Long edge:** 5.2 m from the corner. The other 0.8 m of that edge already
  has a fence.
- **Short edge:** 1.8 m from the corner, ending at the steps, which fill the
  other 1.2 m of that side and are already built.

The deck surface is 0.96 m above the ground at its highest point. Posts bolt
to the outside face of the edge joists. Two posts straddle the corner, one on
each joist face, meeting along the corner's vertical edge. The infill is
vertical balusters between a top and a bottom rail, with a flat cap rail on
top.

## Build

From the repo root:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" balustrade/build.py
```

This writes the following to `out/`, which git ignores:

- `balustrade.FCStd` (open it in FreeCAD to look around the model);
- `balustrade.step`;
- `balustrade_cut_list.csv`.

It also prints the bays, the cut list and the design checks, and exits 1 if
any check fails. Every dimension is a named constant at the top of `build.py`.
Change one, rerun, and the posts, baluster spacing and cut list follow.

## Rules it is built to

From [F4/AS1](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/),
3rd edition, amendment 2, effective 1 January 2017:

| Rule | Source | In `build.py` |
|---|---|---|
| Housing decks: barrier at least 1000 mm high, measured from the finished deck surface | Table 1 | `BARRIER_HEIGHT_MIN` |
| No opening anywhere over the full height lets a 100 mm sphere through | 1.2.1 b) | `MAX_OPENING`, checked for the baluster gaps, the gap under the bottom rail and the corner |
| Vertical balusters: the top of the bottom rail is no more than 200 mm above the deck | Figure 2(a) | `BOTTOM_RAIL_TOP_MAX` |

**Is a barrier required?** Clause F4.3.1 requires one where people could fall
**1 m or more**. MBIE's
[barriers guidance](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/barriers-and-handrails/)
says that where the ground slopes away from a deck, measure the fall 1200 mm
out from the deck. At 0.96 m directly below, the deck may be just under the
threshold. If the ground falls away, measure it 1.2 m out. Either way, this
design meets the F4/AS1 figures above.

## Current design

| Item | Value |
|---|---|
| Barrier height | 1000 mm, top of cap above the deck surface |
| Posts | 8 posts, 90x90, 1175 mm long (220 mm below the deck surface for the bolts) |
| Long run | 5 posts, 4 bays at 1278 mm centres, 8 balusters per bay, 94.6 mm gaps |
| Short run | 3 posts, 2 bays at 855 mm centres, 5 balusters per bay, 92.5 mm gaps |
| Rails | 90x45 on edge. The bottom rail is 50 mm above the deck, with its top at 140 mm; the top rail sits under the cap. |
| Balusters | 42x42, 725 mm long, 42 in total |
| Cap | 140x45, one 5315 mm length and one 1775 mm length butted at the corner |

## Not decided or not checked yet

- **Structure is not checked.** MBIE's
  [Practice Advisory 10](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/practice-advisory-10/)
  says barrier loads from AS/NZS 1170.1, as modified by B1/VM1, apply to
  barriers against falls of 1 m or more. For decks, the loads come from row C3
  of its Table 3.3. It also says the elements a barrier fixes to must carry
  those loads. This model checks geometry only, so these are unchecked:
  - the 1500 mm maximum post spacing;
  - the bolts to the joists;
  - the joists themselves;
  - the rail spans.
- **Gaps leave about 5 mm of margin.** The widest gap is 94.6 mm against the
  100 mm limit. A twisted or shrunk baluster could eat that. Raise
  `GAP_MARGIN` for more room, which adds a baluster per bay.
- **Timber treatment.** The
  [barriers guidance](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/barriers-and-handrails/)
  sets durability (B2/AS1 Table 1): at least 50 years for barrier posts and
  the handrail (the top rail), and at least 15 years for balusters. That
  decides the treatment class.
- **Timber sizes are assumed.** They are common sizes, not chosen ones.
