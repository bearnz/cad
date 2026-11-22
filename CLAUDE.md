# cad

FreeCAD designs for home projects, built from parametric Python scripts.

## Running

`"C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" <design>/build.py` from the
repo root. Output goes to `out/`.

## Testing

Each `build.py` prints its design checks and exits 1 if any fails. Run the
build after every change.

## Notes

- One folder per design. Each design is a Python script that builds the model
  from named dimensions, so changing a dimension and rerunning rebuilds it.
- Scripts run under FreeCAD's own Python, not uv:
  `"C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" <script>.py`
  (FreeCAD 1.1.4 on this PC). Generated `.FCStd` and STL/STEP exports go in
  `out/`, which is ignored.
- Conventions are in ~/.claude/CLAUDE.md (feature branches -> PR -> main,
  push only on approval, provenance labels). The base files came from
  bearnz/project-template; /new-project says how to sync later changes.
