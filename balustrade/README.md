# Deck balustrade

Timber balustrade along two edges of the deck (about 6 m x 3 m). The two runs
meet at a right-angled outside corner:

- **Long edge:** 5.2 m from the corner. The other 0.8 m of that edge already
  has a fence.
- **Short edge:** 1.8 m from the corner, ending at the steps, which fill the
  other 1.2 m of that side and are already built.

The deck surface is 0.96 m above the ground at its highest point.

The design follows MBIE's timber barrier for houses: paragraph 4.2.7 of
[*Guidance on Barrier Design*](https://www.building.govt.nz/assets/Uploads/building-code-compliance/b-stability/b1-structure/guidance-on-barrier-design/barrier-design-guidance.pdf)
(March 2012). It has:

- 90x90 posts bolted to the outside face of the edge joists;
- 90x45 top and bottom rails between the posts;
- 125x25 vertical palings nailed to the deck-side face of the rails, so the
  rails aren't footholds;
- a 140x45 cap rail, which acts as the handrail, laid flat over the posts.

Two posts straddle the corner, one on each joist face. Each is set back from
the corner, so a gap is left between them, and the cap rails run on over the
gap and meet on a 45° mitre at the corner.

**The corner gap is a diagonal.** With each post set back by `CORNER_OFFSET`,
the opening between their nearest edges is `CORNER_OFFSET * sqrt(2)`. By
default the build picks the offset that makes this opening equal to the widest
paling gap. Setting the posts back also shortens the bays, which closes the
paling gaps a little.

## Build

From the repo root:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" balustrade/build.py
```

This builds two versions of the design, which differ only at the corner
(`VARIANTS` in `build.py`):

| Version | Corner joint | Files in `out/` (git ignores them) |
|---|---|---|
| The design | Caps meet on a 45° mitre | `balustrade.FCStd`, `balustrade.step`, `balustrade_cut_list.csv` |
| For comparison | The long cap runs through and the short cap butts onto its side. A 90x90x90 post offcut sits between the two corner posts under the joint, fixed to both posts and up into both caps. | `balustrade_block.FCStd`, `balustrade_block.step`, `balustrade_block_cut_list.csv` |

Open the `.FCStd` files in FreeCAD to look around the models. The build also
prints the bays, and for each version its cut list and design checks. It exits
1 if any check fails. Every dimension is a named constant at the top of `build.py`.
Change one, rerun, and the posts, paling spacing and cut list follow.

## Rules it is built to

From [F4/AS1](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/),
3rd edition, amendment 2, effective 1 January 2017:

| Rule | Source | In `build.py` |
|---|---|---|
| Housing decks: barrier at least 1000 mm high, measured from the finished deck surface | Table 1 | `BARRIER_HEIGHT_MIN` |
| No opening anywhere over the full height lets a 100 mm sphere through | 1.2.1 b) | `MAX_OPENING`, checked for the paling gaps, the gap under the bottom rail and the corner |
| Vertical members: the top of the bottom rail is no more than 200 mm above the deck | Figure 2(a) | `BOTTOM_RAIL_TOP_MAX` |

From MBIE's *Guidance on Barrier Design* (March 2012), paragraph 4.2.7, and
its [barrier guide and updates](https://www.building.govt.nz/building-code-compliance/b-stability/b1-structure/barrier-guide-and-updates)
page (confirmed current in February 2016):

| Rule | In the design |
|---|---|
| A house timber barrier following 4.2.7 meets the Building Code with no further engineering design, if the deck follows NZS 3604:2011 clause 7.4 and the 90x90 posts are at **1000 mm centres at most** | `MAX_POST_SPACING = 1000`, checked |
| Posts 90x90, fixed to a **double** end joist or double boundary joist with **2 × M12 bolts** (50x50x3 washers, heads and nuts not countersunk), as in NZS 3604 Figure 7.10(c) | Posts modelled; bolts and joists not modelled |
| NZS 3604 Figure 7.10(c) corrections: the 250 mm M12 coach screws aren't available, so use 200 mm and 240 mm M12 coach screws at 140 mm centres, as MBIE's page sets out | Not modelled |
| Handrail 90x45, with 4 × 100x3.75 nails into the top of each post | 140x45 cap |
| Top and bottom rails 90x45 between the posts, with 4 skewed 100x3.75 nails at each end, or fixed to a face of the posts | Between the posts |
| Palings 125x25 spanning between the rails, with gaps of 100 mm at most, and 3 × 60x3.15 nails to each rail. Other infill needs specific design. | 125x25 palings |
| All timber SG8 wet (MSG8 or VSG8); palings may be SG6 (No. 1 Framing). Treatment to NZS 3602:2003. Sizes are actual finished sizes. | Finished sizes used |
| Fixings to NZS 3604:2011 section 4.4. Type 304 stainless steel in copper azole or ACQ treated timber. | Not modelled |
| Durability: 50 years for the supporting structure, posts and handrail; 15 years for the palings and rails | Radiata pine H3.2 per [BRANZ](https://www.branz.co.nz/design-build/articles/deck-barriers) |

**Is a barrier required?** Clause F4.3.1 requires one where people could fall
**1 m or more**. MBIE's
[barriers guidance](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/barriers-and-handrails/)
says that where the ground slopes away from a deck, measure the fall 1200 mm
out from the deck. At 0.96 m directly below, the deck may be just under the
threshold. If the ground falls away, measure it 1.2 m out. Either way, this
design meets the figures above.

## Current design

| Item | Value |
|---|---|
| Barrier height | 1000 mm, top of cap above the deck surface |
| Posts | 10 posts, 90x90, 1175 mm long (220 mm below the deck surface for the bolts) |
| Gap margin | Gaps designed at least 15 mm under the 100 mm limit (`GAP_MARGIN`), for timber movement |
| Corner | Each corner post 36.2 mm back from the deck corner; 51.1 mm diagonal opening between them |
| Long run | 7 posts, 6 bays at 846 mm centres, 4 palings per bay, 51.1 mm gaps |
| Short run | 3 posts, 2 bays at 837 mm centres, 4 palings per bay, 49.4 mm gaps |
| Rails | 90x45 on edge, behind the palings. The bottom rail is 50 mm above the deck, with its top at 140 mm; the top rail sits under the cap. |
| Palings | 125x25, 905 mm long (from the underside of the bottom rail to the cap), 32 in total |
| Cap | 140x45, 5315 mm and 1915 mm (to the long point), each with a 45° mitre at the corner end |

## Not decided or not checked yet

- **The deck framing.** MBIE's no-engineer path needs a deck built to NZS 3604
  clause 7.4, with a **double** end or boundary joist behind every post. Check
  both edges of the deck before building.
- **The mitred corner is unsupported.** Each cap runs about 151 mm past the
  face of its corner post to the mitre. The only thing holding the joint is the
  joint itself (glue, screws or a biscuit). The block version supports the
  joint from below. A block also works under a mitre if the joint needs it.
- **Paling count.** At 4 palings per bay the gaps are about 50 mm. Three per
  bay gives about 95 mm, under the 100 mm limit but with only 5 mm of margin,
  so it fails the 15 mm `GAP_MARGIN`.
- **Editions.** The guide is from 2012 and cites NZS 3602:2003 and
  NZS 3604:2011. Whether newer editions change any of this isn't checked.
