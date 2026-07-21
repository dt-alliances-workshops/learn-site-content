import pathlib

from migration.claat.images import process_images

FIX = pathlib.Path(__file__).parent / "fixtures" / "sample_claat" / "img"


def test_rewrites_ref_with_slug_and_prefix():
    body = "![image](img/pic one.png)"
    out, renames, flags = process_images(body, FIX, "img/lab0")
    assert "![" in out and "](img/lab0/pic-one.png)" in out
    assert renames["pic one.png"] == "pic-one.png"


def test_alt_derived_from_filename():
    out, renames, flags = process_images("![image](img/pic one.png)", FIX, "img/lab0")
    assert "![pic one](img/lab0/pic-one.png)" in out
    assert any(f.section == "alt" for f in flags)


def test_missing_image_flagged_blocking():
    out, renames, flags = process_images("![image](img/nope.png)", FIX, "img/lab0")
    assert any(f.section == "blocking" for f in flags)


def test_double_slash_after_img_is_normalized():
    # Real-world source markdown sometimes has a stray extra slash, e.g.
    # `img//aws-event-engine-popup.png`. The capture group must not retain
    # a leading "/" — otherwise pathlib treats `src_img_dir / orig` as an
    # absolute path (discarding src_img_dir), the on-disk existence check
    # always fails, and the image is never copied even though the rewritten
    # markdown link points at it (causing a broken mkdocs --strict build).
    out, renames, flags = process_images("![image](img//pic one.png)", FIX, "img/lab0")
    assert "](img/lab0/pic-one.png)" in out
    assert renames["pic one.png"] == "pic-one.png"
    assert not any(f.section == "blocking" for f in flags)
