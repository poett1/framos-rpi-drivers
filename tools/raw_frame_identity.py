#!/usr/bin/env python3
"""Check that every raw frame in a rpicam-raw --segment capture is byte-identical
to the first one. With the sensor test pattern enabled this catches torn, shifted
or dropped rows from too-small HMAX/VMAX or a front-end overrun.

usage: raw_frame_identity.py DIR [--glob 'f*.raw'] [--stride BYTES]
exit status 0: all frames identical and same size; 1 otherwise.
"""
import argparse, glob, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("--glob", default="f*.raw")
ap.add_argument("--stride", type=int, default=0, help="bytes per row, to report the first bad row")
a = ap.parse_args()

files = sorted(glob.glob(os.path.join(a.dir, a.glob)))
if len(files) < 2:
    sys.exit(f"need at least two frames in {a.dir}, found {len(files)}")

ref = open(files[0], "rb").read()
bad, sizes = [], {len(ref)}
for f in files[1:]:
    b = open(f, "rb").read()
    sizes.add(len(b))
    if b != ref:
        off = next((i for i, (x, y) in enumerate(zip(ref, b)) if x != y), min(len(ref), len(b)))
        bad.append((os.path.basename(f), off, off // a.stride if a.stride else -1))

print(f"frames={len(files)} sizes={sorted(sizes)} differing={len(bad)}")
for name, off, row in bad[:10]:
    print(f"  {name}: first difference at byte {off}" + (f" (row {row})" if row >= 0 else ""))
sys.exit(1 if bad or len(sizes) != 1 else 0)
