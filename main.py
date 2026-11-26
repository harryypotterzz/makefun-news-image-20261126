#!/usr/bin/env python3
"""Entry program for the Make.fun news-image bounty (26 November 2026).

The grader runs this program with no network. It writes the
pre-rendered news image (entry.png, in this repository) to the
output directory as entry.png.

Standard library only. Deterministic: every run writes the exact
same bytes. The output directory is taken from $MAKEFUN_OUTPUT_DIR
when set, otherwise /output. Its contents are cleared first, but
the directory itself is never removed (the grader runs as a
different user and /output may be a mount point).
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"


def empty_directory(directory):
    """Delete everything inside directory; keep the directory itself."""
    for item in directory.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()


def main():
    if not IMAGE.is_file():
        print(f"error: {IMAGE} is missing", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        empty_directory(out_dir)
        shutil.copyfile(IMAGE, out_dir / "entry.png")
    except OSError as exc:
        print(f"error: cannot write output: {exc}", file=sys.stderr)
        return 1

    # Confirm the copy is complete: the grader gates on the exact bytes.
    if (out_dir / "entry.png").stat().st_size != IMAGE.stat().st_size:
        print("error: copied file size differs from source", file=sys.stderr)
        return 1

    print(f"wrote {out_dir / 'entry.png'} ({IMAGE.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
