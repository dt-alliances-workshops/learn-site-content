import json
import pathlib

import yaml

from migration.convert import convert_family


def _make_family(tmp_path):
    fam = tmp_path / "src" / "demo"
    for i, dur in ((0, 3), (10, 5)):
        d = fam / f"demo-lab{i}"
        (d / "img").mkdir(parents=True)
        (d / "img" / "pic.png").write_bytes(b"x")
        (d / "README.md").write_text(
            f"id: demo-lab{i}\nsummary: s{i}\n\n"
            f"# Demo Lab {i}\n\n## Step\nDuration: {dur}\n\n"
            f"![image](img/pic.png)\n"
        )
    return fam


def _scaffold_stub(out):
    (out / "docs").mkdir(parents=True)
    (out / "mkdocs.yaml").write_text('site_name: "x"\nnav:\n# NAV_PLACEHOLDER\n')


def test_convert_family_orders_labs_naturally(tmp_path):
    fam = _make_family(tmp_path)
    out = tmp_path / "out"
    _scaffold_stub(out)
    log = convert_family(fam, out, strip_prefix="demo-")
    pages = [l["page"] for l in log["labs"]]
    # lab0 before lab10 despite lexical order
    assert pages == ["docs/1-lab0.md", "docs/2-lab10.md"]


def test_convert_family_writes_pages_images_and_nav(tmp_path):
    fam = _make_family(tmp_path)
    out = tmp_path / "out"
    _scaffold_stub(out)
    convert_family(fam, out, strip_prefix="demo-")
    assert (out / "docs" / "1-lab0.md").exists()
    assert (out / "docs" / "img" / "lab0" / "pic.png").exists()
    nav = (out / "mkdocs.yaml").read_text()
    assert "1-lab0.md" in nav and "NAV_PLACEHOLDER" not in nav
    log = json.loads((out / "transform_log.json").read_text())
    assert any(f["section"] == "screenshot" for f in log["labs"][0]["flags"])


def test_convert_family_escapes_quotes_in_title_for_nav(tmp_path):
    fam = tmp_path / "src" / "demo"
    d = fam / "demo-lab0"
    (d / "img").mkdir(parents=True)
    (d / "README.md").write_text(
        'id: demo-lab0\nsummary: s0\n\n'
        '# Demo "Quoted" Lab\n\n## Step\nDuration: 3\n\n'
    )
    out = tmp_path / "out"
    _scaffold_stub(out)

    convert_family(fam, out, strip_prefix="demo-")

    nav_text = (out / "mkdocs.yaml").read_text()
    # The generated mkdocs.yaml must remain valid YAML even though the
    # source lab title contains a double quote.
    parsed = yaml.safe_load(nav_text)
    assert parsed is not None
    # The escaped title should still be recoverable from the nav.
    assert 'Demo \\"Quoted\\" Lab' in nav_text
