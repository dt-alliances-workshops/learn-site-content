import argparse
import json
import pathlib
import sys

from migration.registry import find_orphans

_COUNT_ORDER = ["blocking", "env", "screenshot", "alt", "judgment"]


def _counts(log: dict) -> dict:
    c = {k: 0 for k in _COUNT_ORDER}
    for lab in log["labs"]:
        for f in lab["flags"]:
            if f["section"] in c:
                c[f["section"]] += 1
    return c


def build_tracker(logs: list[dict], orphans: list[str], out_dir) -> str:
    out_dir = pathlib.Path(out_dir)
    lines = [
        "# CLaaT Migration Tracker",
        "",
        "One row per generated workshop repo on this branch. Fill in **Assignee**, "
        "update **Status** as you go. Definition of done per repo: all REVIEW.md "
        "boxes checked + `mkdocs build --strict` clean, committed to the branch "
        "(no PR to main).",
        "",
        "| Workshop | Repo | Labs | Blocking | Env | Screenshot | Alt | Judgment | Assignee | Status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for log in logs:
        c = _counts(log)
        lines.append(
            f"| {log['workshop']} | {log['repo']} | {len(log['labs'])} | "
            f"{c['blocking']} | {c['env']} | {c['screenshot']} | {c['alt']} | "
            f"{c['judgment']} | TODO | not started |"
        )
    lines += ["", "## Unassigned labs (claimed by no workshop)", ""]
    if orphans:
        lines += [f"- {name}" for name in orphans]
    else:
        lines.append("none")
    lines.append("")
    md = "\n".join(lines)
    (out_dir / "MIGRATION-TRACKER.md").write_text(md)
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build MIGRATION-TRACKER.md from generated repos.")
    ap.add_argument("--out", required=True, help="dir containing generated repos")
    ap.add_argument("--corpus", default="workshop-markdown")
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    logs = []
    for tl in sorted(out.glob("*/transform_log.json")):
        logs.append(json.loads(tl.read_text()))
    build_tracker(logs, find_orphans(args.corpus), out)
    print(f"Wrote {out/'MIGRATION-TRACKER.md'} ({len(logs)} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
