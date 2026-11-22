# Deck

The existing deck, modelled so the balustrade can be fitted to it. It isn't a
design for a new deck: it records what's there, and marks what hasn't been
measured.

It uses the same coordinates as the balustrade. The origin is the outside
corner where the two balustraded edges meet, the long edge runs along +X, the
short edge along +Y, and z = 0 is the deck surface.

## What it models

| Item | Value | Source |
|---|---|---|
| Size | 6000 x 3000 mm | About 6 m x 3 m, reported |
| Height | Deck surface 960 mm above the ground at its highest | Reported |
| Joists | 190x45, running along the short edge | Reported |
| Long edge (y = 0) | Double **boundary joist**, across the joist ends | Reported doubled |
| Short edge (x = 0) | Double **edge joist**, parallel to the joists | Reported doubled |
| Far edges | Single boundary and edge joists | Not checked |
| Decking | 90x19 hardwood, running along the long edge, flush with the outside of the framing | Reported hardwood; size, gap and overhang are placeholders |
| Joist positions | Evenly spaced at 450 mm centres at most (422 mm) | **Placeholder** |

The joist names follow MBIE's *Guidance on Barrier Design*, 1.2: a boundary
joist runs across the outer ends of the joists, and an edge joist is the
outermost joist, parallel to the others.

The model leaves out the bearers, piles and steps, and joins in the boards.
None of them touch the balustrade fixings.

## Build

From the repo root:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" deck/build.py
```

Writes `out/deck.FCStd`, `out/deck.step` and `out/deck_cut_list.csv`. It prints
the joist centres, the cut list and the checks (joist spacing, decking cover,
doubled edges).

## To measure

- **Joist centres along the long edge**, from the corner: set
  `JOIST_CENTRES` to the list. These decide where the long run's post bolts
  can go (see [deck_with_balustrade](../deck_with_balustrade/)).
- **Blocking** between the short edge's double edge joist and the next joist.
  The model has none. Any there could get in the way of the short run's nuts.
- **The decking**: board width and thickness, the gap, and whether the boards
  overhang the framing (`DECKING_OVERHANG`). Boards that overhang would need
  notching round the posts.
