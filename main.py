"""make.fun news-image-20261124 entry: copy the pre-rendered infographic to the output.

Python 3.13 standard library only, no network, deterministic: the same bytes every run.
The image itself is drawn by tools/make_image.py and committed as entry.png.
"""
import os
import shutil

here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
shutil.copyfile(os.path.join(here, "entry.png"), os.path.join(out_dir, "entry.png"))
