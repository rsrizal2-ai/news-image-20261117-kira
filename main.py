"""Copy the finished news poster into the grader output directory.

The poster is built ahead of time by render_poster.py and stored beside
this file as entry.png. This program only copies those exact bytes to
the output location, so repeated runs always produce identical output.
It uses only the Python standard library and never touches the network.
"""

import os
import shutil
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        raise FileNotFoundError(f"poster image not found beside entrypoint: {source}")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    if target.stat().st_size != source.stat().st_size:
        raise OSError("copied poster size does not match the source image")


if __name__ == "__main__":
    main()
