# cad

FreeCAD designs for home projects, built from parametric Python scripts.

## Designs

- [balustrade](balustrade/): a timber balustrade for two edges of the deck
- [deck](deck/): the existing deck's framing and boards
- [deck_with_balustrade](deck_with_balustrade/): the two together, with the
  bolts that fix the posts to the deck

## Running

Each design has a `build.py` that runs under FreeCAD's own Python. From the
repo root:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" <design>/build.py
```

Output (`.FCStd`, STEP and a cut list) goes to `out/`, which git ignores.

## Testing

There is no separate test suite. Each `build.py` prints its design checks and
exits 1 if any fails. A check that waits on a measurement prints TODO and
doesn't fail the build.

## Copyright

Copyright (c) 2026 Josh (github.com/bearnz). All rights reserved.

No licence is granted. You are welcome to read this code and to fork it on
GitHub; you may not use, copy, modify or redistribute it without permission.
See [NOTICE](NOTICE) for the terms, and open an issue if you would like to use
any of it.
