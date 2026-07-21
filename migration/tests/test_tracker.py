import pathlib

from migration.tracker import build_tracker


def _log(repo, workshop, sections_per_lab):
    return {"repo": repo, "workshop": workshop,
            "labs": [{"flags": [{"section": s, "message": "", "locator": "", "line": 0}
                                for s in secs]} for secs in sections_per_lab]}


def test_tracker_counts_and_rows(tmp_path):
    logs = [
        _log("enablement-aws-selfpaced", "aws-selfpaced",
             [["blocking", "env", "screenshot"], ["alt", "screenshot"]]),
    ]
    md = build_tracker(logs, ["aws-dt-lab0-Prereq"], tmp_path)
    assert "| aws-selfpaced |" in md
    assert "enablement-aws-selfpaced" in md
    # 2 labs, 1 blocking, 1 env, 2 screenshot, 1 alt, 0 judgment
    assert "| 2 | 1 | 1 | 2 | 1 | 0 |" in md
    assert "TODO" in md          # assignee placeholder
    assert (tmp_path / "MIGRATION-TRACKER.md").exists()


def test_tracker_lists_orphans(tmp_path):
    md = build_tracker([_log("r", "w", [["alt"]])], ["aws-dt-lab0-Prereq"], tmp_path)
    assert "## Unassigned labs" in md
    assert "aws-dt-lab0-Prereq" in md


def test_tracker_no_orphans(tmp_path):
    md = build_tracker([_log("r", "w", [["alt"]])], [], tmp_path)
    assert "none" in md.lower()
