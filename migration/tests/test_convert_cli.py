import json
import pathlib

import yaml

from migration.convert import convert_workshop
from migration.registry import Workshop


def _make_corpus(tmp_path):
    corpus = tmp_path / "corpus"
    specs = [
        ("demo-lab0", 3, "aws-immersion-day,aws-selfpaced"),
        ("demo-lab10", 5, "aws-selfpaced"),
    ]
    for name, dur, tags in specs:
        d = corpus / name
        (d / "img").mkdir(parents=True)
        (d / "img" / "pic.png").write_bytes(b"x")
        (d / "README.md").write_text(
            f"id: {name}-id\ntags: {tags}\n\n# Demo {name}\n\n"
            f"## Step\nDuration: {dur}\n\nOpen the Azure Portal.\n\n"
            f"![image](img/pic.png)\n"
        )
    return corpus


def _scaffold_stub(out):
    (out / "docs").mkdir(parents=True)
    (out / "mkdocs.yaml").write_text('site_name: "x"\nnav:\n# NAV_PLACEHOLDER\n')


def test_convert_workshop_selects_by_tag_and_orders(tmp_path):
    corpus = _make_corpus(tmp_path)
    out = tmp_path / "out"
    _scaffold_stub(out)
    w = Workshop("demo-self", "enablement-demo-self", "Demo Self",
                 "tag", "aws-selfpaced", ["aws"], "1h")
    log = convert_workshop(w, corpus, out)
    pages = [l["page"] for l in log["labs"]]
    # both labs carry aws-selfpaced; natural order lab0 before lab10
    assert pages == ["docs/1-demo-lab0.md", "docs/2-demo-lab10.md"]


def test_convert_workshop_writes_pages_images_id_and_flags(tmp_path):
    corpus = _make_corpus(tmp_path)
    out = tmp_path / "out"
    _scaffold_stub(out)
    w = Workshop("demo-imm", "enablement-demo-imm", "Demo Imm",
                 "tag", "aws-immersion-day", ["aws"], "1h")
    log = convert_workshop(w, corpus, out)
    # only lab0 has aws-immersion-day
    assert [l["source"] for l in log["labs"]] == ["demo-lab0"]
    assert (out / "docs" / "1-demo-lab0.md").exists()
    assert (out / "docs" / "img" / "demo-lab0" / "pic.png").exists()
    lab = log["labs"][0]
    assert lab["id"] == "demo-lab0-id"
    sections = {f["section"] for f in lab["flags"]}
    assert {"env", "screenshot", "judgment"} <= sections  # env from cloud-prose scan
    nav = (out / "mkdocs.yaml").read_text()
    assert "1-demo-lab0.md" in nav and "NAV_PLACEHOLDER" not in nav


def test_convert_workshop_escapes_quotes_in_title_for_nav(tmp_path):
    # Regression test: lab title with double-quotes must be escaped in YAML nav
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    lab_dir = corpus / "quote-lab"
    (lab_dir / "img").mkdir(parents=True)
    (lab_dir / "img" / "pic.png").write_bytes(b"x")
    (lab_dir / "README.md").write_text(
        'id: quote-lab-id\ntags: demo-tag\n\n# Deploy the "Astroshop" demo\n\n'
        '## Step\nDuration: 5\n\nOpen the portal.\n\n'
        '![image](img/pic.png)\n'
    )
    out = tmp_path / "out"
    _scaffold_stub(out)
    w = Workshop("demo", "enablement-demo", "Demo", "tag", "demo-tag", ["x"], "1h")
    log = convert_workshop(w, corpus, out)
    # Verify the mkdocs.yaml was generated
    assert len(log["labs"]) == 1
    # Parse the generated mkdocs.yaml; this will raise if quotes are not escaped
    mk_yaml = (out / "mkdocs.yaml").read_text()
    parsed = yaml.safe_load(mk_yaml)
    # Confirm the nav structure is valid
    assert "nav" in parsed
    assert parsed["nav"] is not None
