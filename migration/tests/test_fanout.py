import pathlib

from migration.fanout import run_fanout
from migration.registry import Workshop


def _corpus(tmp_path):
    corpus = tmp_path / "corpus"
    for name in ("demo-lab0", "demo-lab1"):
        d = corpus / name
        (d / "img").mkdir(parents=True)
        (d / "img" / "pic.png").write_bytes(b"x")
        (d / "README.md").write_text(
            f"id: {name}\ntags: demo-tag\n\n# Demo {name}\n\n## Step\nDuration: 2\n\n"
            f"![image](img/pic.png)\n"
        )
    return corpus


def test_run_fanout_builds_repo_review_and_tracker(tmp_path):
    corpus = _corpus(tmp_path)
    out = tmp_path / "out"
    ws = [Workshop("demo", "enablement-demo", "Demo Workshop",
                   "tag", "demo-tag", ["demo"], "1h")]
    results = run_fanout(ws, corpus, out, build=False)
    assert results[0]["workshop"] == "demo"
    assert results[0]["labs"] == 2
    assert results[0]["build_ok"] is None       # build disabled
    assert (out / "enablement-demo" / "REVIEW.md").exists()
    assert (out / "enablement-demo" / "REVIEW-repos-snippet.yaml").exists()
    assert (out / "enablement-demo" / "docs" / "1-demo-lab0.md").exists()
    assert (out / "MIGRATION-TRACKER.md").exists()
