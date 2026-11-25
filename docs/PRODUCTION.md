# MeshEngine production rules
Public CI is solely for generic engine development and synthetic fixtures. No commercial assets, character-specific scripts, private repository credentials, or private renders may enter public CI, logs, artifacts, caches or commits. Private production runs locally or on separately authorised private compute; do not use public Actions to bypass private usage limits.
Pipeline: brief -> references -> blockout -> multi-angle actual mesh renders -> human/AI review and revision -> print engineering -> geometry and slicer checks -> private packaging -> physical test and rights review.
A geometry pass is not a printability certification. Never claim physical testing without evidence.
Run: blender -b -t 2 --python-exit-code 1 --python scripts/smoke.py
Outputs: build/fixture.blend, fixture.stl, four PNG renders and report.json. STL coordinates are millimetres. 3MF, slicer and artistic review automation are later phases.
