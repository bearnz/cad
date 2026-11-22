# Deck with balustrade

The [deck](../deck/) and the [balustrade](../balustrade/) (the mitred version)
in one model, with the bolts that fix each post to the deck framing. It builds
both from their own scripts, so a change to either shows up here.

## How the posts attach

From MBIE's *Guidance on Barrier Design* (March 2012), 4.2.7.2 and
Figure 4.8:

- Each 90x90 post is fixed to the **double** joist behind it with **two M12
  bolts**: through the post and both plies, with a 50x50x3 washer under the
  head and the nut. Heads and nuts aren't countersunk.
- One bolt is 25 mm below the top of the joist and the other 25 mm above its
  bottom. On these 190 mm joists, under 19 mm decking, that puts them 44 mm and
  184 mm below the deck surface, 140 mm apart.
- The post's bottom is flush with the bottom of the joist.
- The deck under it follows NZS 3604:2011 section 7.4, and the post is
  positioned as in its Figure 7.10(c).

The bolts go through 186 mm: the post, two 45 mm plies and two washers. With
a nut and two threads showing, that's **M12 x 210** bolts, 20 of them. The
length is rounded up to 10 mm; check what the merchant stocks. Use Type 304
stainless in treated timber (4.2.7, see the balustrade README).

The nut and inside washer need room on the deck side of the framing.

- **Short edge:** the double edge joist runs parallel to the joists, so behind
  it is open.
- **Long edge:** the double boundary joist has the joist ends butting into
  it, and a nut can't go where a joist end is.

For each post, the build looks for the bolt position nearest the middle of
the post that leaves the hardware at least 2 mm clear of other framing and
bolts. It moves the bolts at most 15 mm off the post's centre, which keeps
them 30 mm from the side of the post.

## Build

From the repo root:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" deck_with_balustrade/build.py
```

Writes `out/deck_with_balustrade.FCStd`, `.step` and `_fixings.csv`, the last
with each post's bolt position. It prints the same table and the checks: the
runs fit the deck, the posts are flush with the joist bottom and bear on the
framing, every post has a bolt position, the bolts clear the joists, and
nothing else overlaps.

## Where it stands

With the placeholder joist spacing (deck/build.py):

| Post | Bolts along the run | Off the post's centre | |
|---|---|---|---|
| Long 0 (corner) | 117 mm | +8 mm | Clears the edge joist and the short run's corner nuts |
| Long 1 | 961 mm | +12 mm | Clears a joist end |
| Long 2 | 1806 mm | +15 mm | Clears a joist end, at the limit |
| Long 3 to 6 | | | **A joist end behind every position** (TODO) |
| Short 0 (corner) | 120 mm | +12 mm | Clears the long run's corner nuts |
| Short 1, 2 | | 0 | Open behind |

The long-run posts are at 841 mm centres and the placeholder joists at 422,
so a post lands near a joist end every other bay or so. This depends entirely
on where the real joists are, so the check prints TODO, not FAIL, until
`JOIST_CENTRES` is measured. Once measured, a post with a joist behind it
could:

1. **Move.** The posts are at 841 mm centres against a limit of 1000, so
   there's room to shift a post into the joist bay next to it. The palings in
   the bays either side follow.
2. **Have its bolts moved further off-centre**, if a closer edge distance in
   the post is acceptable (`MIN_BOLT_EDGE_IN_POST`, a placeholder).

At the corner, both runs' nuts meet in the inside corner of the framing. That
is why the corner bolts sit 8 mm and 12 mm off-centre, away from the corner.

## Not checked yet

- **NZS 3604:2011 Figure 7.10(c).** 4.2.7.2 says to position the posts as in
  this figure. Not read: it's in the standard, not the guide. MBIE's
  [barrier guide and updates](https://www.building.govt.nz/building-code-compliance/b-stability/b1-structure/barrier-guide-and-updates)
  page says it shows straps with two M12 x 240 mm coach screws at the joist
  ends and nogs, 140 mm apart vertically. It may say where posts go relative
  to the joist ends and nogs, which could change the approach above. Read it
  before drilling.
- **Edge distances.** Figure 4.8's 25 mm puts each washer's edge flush with
  the top or bottom of the joist. `MIN_BOLT_EDGE_IN_POST` (30 mm) and the
  2 mm clearance aren't from the guide.
- **Hardware sizes.** The head, nut and thread allowance are approximate.
  They are used only for clearances and the bolt length.
- **Spanner room** round the nuts under the deck isn't modelled.
