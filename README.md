# cad

FreeCAD designs for home projects, built from parametric Python scripts.

## Designs

- [balustrade](balustrade/): a timber balustrade for two edges of the deck

## Running

Each design has a `build.py` that runs under FreeCAD's own Python. From the
repo root:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" <design>/build.py
```

Output (`.FCStd`, STEP and a cut list) goes to `out/`, which git ignores.

## Testing

There is no separate test suite. Each `build.py` prints its design checks and
exits 1 if any fails.
