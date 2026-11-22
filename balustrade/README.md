# Deck balustrade

Timber balustrade along two edges of the deck (about 6 m x 3 m). The two runs
meet at a right-angled outside corner:

- **Long edge:** 5.2 m from the corner. The other 0.8 m of that edge already
  has a fence.
- **Short edge:** 1.8 m from the corner, ending at the steps, which fill the
  other 1.2 m of that side and are already built.

The deck surface is 0.96 m above the ground at its highest point, and the
ground doesn't slope away within the property. The barrier is there to keep
small children from falling off the deck.

The design is based on MBIE's timber barrier for houses: paragraph 4.2.7 of
[*Guidance on Barrier Design*](https://www.building.govt.nz/assets/Uploads/building-code-compliance/b-stability/b1-structure/guidance-on-barrier-design/barrier-design-guidance.pdf)
(March 2012). It has:

- 90x90 posts bolted to the outside face of the edge joists;
- 90x45 top and bottom rails between the posts;
- **75x25** vertical palings on the deck-side face of the rails, so the rails
  aren't footholds. 4.2.7 uses 125x25; see below.
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
| Palings 125x25 spanning between the rails, with gaps of 100 mm at most, and 3 × 60x3.15 nails to each rail. Other infill needs specific design. | **Departs:** 75x25 palings. See "Is a barrier required?" below. |
| All timber SG8 wet (MSG8 or VSG8); palings may be SG6 (No. 1 Framing). Treatment to NZS 3602:2003. Sizes are actual finished sizes. | Finished sizes used |
| Fixings to NZS 3604:2011 section 4.4. Type 304 stainless steel in copper azole or ACQ treated timber. | Not modelled |
| Durability: 50 years for the supporting structure, posts and handrail; 15 years for the palings and rails | Radiata pine H3.2 per [BRANZ](https://www.branz.co.nz/design-build/articles/deck-barriers) |

**Is a barrier required?** No, so this one is voluntary. Clause F4.3.1
requires a barrier where people could fall **1 m or more**. MBIE's
[barriers guidance](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/barriers-and-handrails/)
adds the 1200 mm-out measurement only where the ground slopes away from a
deck. This deck is at most 0.96 m high on flat ground, so the fall is under
1 m everywhere. MBIE's
[Practice Advisory 10](https://www.building.govt.nz/building-code-compliance/f-safety-of-users/f4-safety-from-falling/practice-advisory-10/)
applies the barrier loads to barriers against falls of 1 m or more. Whether
a voluntary barrier needs to meet them is not confirmed.

The design still meets the F4/AS1 figures above (height, 100 mm openings,
bottom rail), because those are what keep a small child from falling
through. Departing from 4.2.7's 125x25 palings means 4.2.7 no longer stands
as proof of strength for the infill. A rough comparison, which is arithmetic
and not a design check:

- **Spread load:** a paling's bending strength scales with its width, so a
  75 mm paling has 0.6 times a 125 mm one's. It also carries load from a
  narrower strip (paling plus gap, 165 mm against 219 mm). Net, about 80% of
  the 125x25 margin.
- **Point load:** Practice Advisory 10 (Figure 22) lets a concentrated load
  be split between two neighbouring members when they're under 100 mm wide
  with gaps under 100 mm. 75 mm palings qualify and 125 mm ones don't, so
  about 120% of the 125x25 margin.

## Current design

| Item | Value |
|---|---|
| Barrier height | 1000 mm, top of cap above the deck surface |
| Posts | 10 posts, 90x90, 1175 mm long (220 mm below the deck surface for the bolts) |
| Gap margin | Gaps designed at least 5 mm under the 100 mm limit (`GAP_MARGIN`), for a more open look |
| Corner | Each corner post 63.8 mm back from the deck corner; 90.2 mm diagonal opening between them |
| Long run | 7 posts, 6 bays at 841 mm centres, 4 palings per bay, 90.2 mm gaps |
| Short run | 3 posts, 2 bays at 823 mm centres, 4 palings per bay, 86.6 mm gaps |
| Rails | 90x45 on edge, behind the palings. The bottom rail is 50 mm above the deck, with its top at 140 mm; the top rail sits under the cap. |
| Palings | 75x25, 905 mm long (from the underside of the bottom rail to the cap), 32 in total. About 60% of each bay is open. |
| Cap | 140x45, 5315 mm and 1915 mm (to the long point), each with a 45° mitre at the corner end |

## Not decided or not checked yet

- **The deck framing.** 4.2.7's posts bolt to a **double** end or boundary
  joist on a deck built to NZS 3604 clause 7.4. Check both edges of the deck
  before building. The posts take the load from anyone leaning on the cap.
- **Paling fixings.** 4.2.7's 3 × 60x3.15 nails per rail are sized for a 125 mm
  board. A 75 mm board has less room before it splits, so pre-drill, or use
  stainless screws. Fixings are more likely to fail than the timber. Check the
  merchant stocks 75x25 in H3.2.
- **The steps.** The 1.2 m opening at the top of the steps is outside this
  model. For toddlers, consider a gate there. The Building Code (clause D1)
  requires handrails on stairs.
- **The mitred corner is unsupported.** Each cap runs about 179 mm past the
  face of its corner post to the mitre. The only thing holding the joint is the
  joint itself (glue, screws or a biscuit). The block version supports the
  joint from below. A block also works under a mitre if the joint needs it.
- **Little room for timber movement.** The widest gap is 90.2 mm against the
  100 mm limit, about 10 mm of margin. A paling that shrinks, cups or is fixed
  slightly off its mark eats into that. Set out the palings with a spacer
  block, and check the gaps after the timber has dried.
- **Editions.** The guide is from 2012 and cites NZS 3602:2003 and
  NZS 3604:2011. Whether newer editions change any of this isn't checked.
