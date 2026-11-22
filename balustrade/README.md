# Deck balustrade

Timber balustrade along two edges of the deck (about 6 m x 3 m). The two runs
meet at a right-angled outside corner:

- **Long edge:** 5.2 m from the corner.
- **Short edge:** 1.8 m from the corner, ending at the steps, which fill the
  other 1.2 m of that side and are already built.

The deck surface is 0.96 m above the ground at its highest point. Posts bolt
to the outside face of the edge joists. The infill is vertical balusters
between a top and a bottom rail, with a flat cap rail on top.

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

## Current design

| Item | Value |
|---|---|
| Barrier height | 1000 mm, top of cap above the deck surface |
| Posts | 90x90, 1175 mm long (220 mm below the deck surface for the bolts) |
| Long run | 5 posts, 4 bays at 1300 mm centres, 9 balusters per bay, 83 mm gaps |
| Short run | 2 more posts plus the shared corner post, 2 bays at 900 mm centres, 6 balusters per bay, 80 mm gaps |
| Rails | 90x45 on edge. The bottom rail is 50 mm above the deck; the top rail sits under the cap. |
| Balusters | 42x42, 725 mm long, 48 in total |
| Cap | 140x45, one 5315 mm length and one 1775 mm length butted at the corner |

## Not decided or not checked yet

- **The building rules are not confirmed.** These figures came from search
  summaries, not from F4/AS1 itself:
  - the 1000 mm height;
  - the rule that no gap may pass a 100 mm sphere;
  - the 150 to 760 mm zone with no footholds.

  I also couldn't confirm from F4/AS1 whether a barrier is required at a
  0.96 m fall: the summaries say it is required over 1.0 m. Fall height is
  measured to the lowest ground a person could land on, so a slope away from
  the deck counts. Check the current
  [F4 Acceptable Solution](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/)
  before buying timber.
- **Structure is not checked.** The 1500 mm maximum post spacing, the bolt
  fixing to the joists, and the rail and cap spans need checking against
  barrier loads (clause B1). This model checks geometry only.
- **The corner post** sits outside both joist faces, so it touches the deck
  only at the joists' corner. It needs blocking or a different fixing detail.
- **Timber sizes and treatment are assumed.** They are common sizes, not
  chosen ones.
- **The remaining 0.8 m of the long edge** has no balustrade in this model.
