import argparse
import pathlib
import subprocess
import sys

from migration.convert import convert_workshop
from migration.registry import WORKSHOPS, find_orphans, get_workshop
from migration.review import build_review, repos_yaml_snippet
from migration.scaffold import scaffold_repo
from migration.tracker import build_tracker


def run_fanout(
    workshops,
    corpus_dir,
    out_dir,
    *,
    build=True,
    template_dir="../enablement-codespaces-template",
    framework_dir="../codespaces-framework",
) -> list[dict]:
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    logs = []
    for w in workshops:
        repo = out_dir / w.repo_name
        scaffold_repo(
            repo,
            site_name=f"Dynatrace Enablement Lab: {w.title}",
            repo_url=f"https://github.com/dynatrace-wwse/{w.repo_name}",
            template_dir=template_dir,
            framework_dir=framework_dir,
        )
        log = convert_workshop(w, corpus_dir, repo)
        logs.append(log)
        build_review(log, repo)
        (repo / "REVIEW-repos-snippet.yaml").write_text(
            repos_yaml_snippet(log, w.repo_name, w.title, w.tags, w.duration)
        )
        build_ok = None
        output = ""
        if build:
            proc = subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict"],
                cwd=repo, capture_output=True, text=True,
            )
            build_ok = proc.returncode == 0
            if not build_ok:
                output = proc.stdout + proc.stderr
        results.append({
            "workshop": w.name, "repo": w.repo_name,
            "labs": len(log["labs"]), "build_ok": build_ok, "build_output": output,
        })
    build_tracker(logs, find_orphans(corpus_dir), out_dir)
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run the CLaaT workshop fan-out.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--corpus", default="workshop-markdown")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated workshop names")
    args = ap.parse_args(argv)
    names = [n.strip() for n in args.only.split(",") if n.strip()]
    workshops = [get_workshop(n) for n in names] if names else WORKSHOPS
    results = run_fanout(workshops, args.corpus, args.out, build=not args.no_build)
    for r in results:
        status = {True: "OK", False: "FAIL", None: "skip"}[r["build_ok"]]
        print(f"[{status}] {r['repo']}: {r['labs']} labs")
        if r["build_ok"] is False:
            print(r["build_output"])
    failed = [r for r in results if r["build_ok"] is False]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
