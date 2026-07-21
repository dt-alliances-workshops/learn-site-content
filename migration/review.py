import argparse
import json
import pathlib
import sys

_SECTION_TITLES = {
    "blocking": "## 1. Blocking — must resolve before committing the branch",
    "screenshot": "## 2. Run & re-capture (validates technical accuracy)",
    "alt": "## 3. Alt-text review (batch-approvable)",
    "judgment": "## 4. Judgment calls (does this lab still belong?)",
}
_ORDER = ["blocking", "screenshot", "alt", "judgment"]


def _items(log: dict, section: str) -> list[str]:
    out = []
    for lab in log["labs"]:
        for f in lab["flags"]:
            if f["section"] != section:
                continue
            loc = lab["page"]
            if f.get("line"):
                loc += f":{f['line']}"
            out.append(f"- [ ] {loc} — {f['message']}")
    return out


def build_review(log: dict, repo_dir) -> str:
    repo_dir = pathlib.Path(repo_dir)
    total_min = sum(l["total_minutes"] for l in log["labs"])
    authors = sorted({l["metadata"].get("authors", "") for l in log["labs"]} - {""})
    lines = [
        f"# Migration Review — {log['repo']}",
        "",
        "Auto-generated. Check boxes as you resolve. The repo already passed "
        "`mkdocs build --strict` at generation.",
        "",
        "## 0. Context (read once)",
        f"- Labs: {len(log['labs'])}  |  Total duration in source: {total_min} min",
        f"- Authors carried over: {', '.join(authors) or 'none'}",
        "- Environment model: DOCS-FIRST (no cloud provisioning; prose references "
        "the learner's own cloud account).",
        "- Lab → page map:",
    ]
    for lab in log["labs"]:
        lines.append(f"    - {lab['source']} → {lab['page']} ({lab['image_count']} images)")
    lines.append("")

    for section in _ORDER:
        items = _items(log, section)
        lines.append(f"{_SECTION_TITLES[section]}  ({len(items)} items)")
        lines.extend(items or ["- (none)"])
        lines.append("")

    lines += [
        "## 5. Definition of done",
        "- [ ] All boxes above checked",
        "- [ ] `mkdocs build --strict` still clean",
        "- [ ] repos.yaml snippet reviewed (see REVIEW-repos-snippet.yaml) — "
        "**do NOT register until the owner lifts the branch-only hold**",
        "- [ ] Work committed to a branch (no PR to main at this time)",
        "",
    ]
    md = "\n".join(lines)
    (repo_dir / "REVIEW.md").write_text(md)
    return md


def repos_yaml_snippet(log, repo_name, title, tags, duration) -> str:
    return (
        f"  - name: {repo_name}\n"
        f"    repo: dynatrace-wwse/{repo_name}\n"
        f"    status: active\n"
        f"    maintainer: \"@TODO\"\n"
        f"    description: \"TODO one-line description\"\n"
        f"    tags: [{', '.join(tags)}]\n"
        f"    title: \"{title}\"\n"
        f"    primary_tag: {tags[0] if tags else 'devops'}\n"
        f"    duration: \"{duration}\"\n"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build REVIEW.md from a transform log.")
    ap.add_argument("repo_dir")
    ap.add_argument("--title", required=True)
    ap.add_argument("--tags", default="devops")
    ap.add_argument("--duration", default="TBD")
    args = ap.parse_args(argv)
    repo_dir = pathlib.Path(args.repo_dir)
    log = json.loads((repo_dir / "transform_log.json").read_text())
    build_review(log, repo_dir)
    snip = repos_yaml_snippet(
        log, repo_dir.name, args.title, args.tags.split(","), args.duration
    )
    (repo_dir / "REVIEW-repos-snippet.yaml").write_text(snip)
    print(f"Wrote {repo_dir/'REVIEW.md'} and repos.yaml snippet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
