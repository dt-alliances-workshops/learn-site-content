# CLaaT Fan-Out Run Implementation Plan (Plan 2 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use the hardened toolkit to generate all 7 workshop repos into `migration/out/`, each passing `mkdocs build --strict`, then commit the generated repo source + `MIGRATION-TRACKER.md` on the branch for teammate validation.

**Architecture:** Add a thin reproducible driver `migration/fanout.py` that reads the `WORKSHOPS` registry and runs scaffold→convert→review→strict-build for each workshop, then builds the tracker. Adjust `.gitignore` to track generated repo *source* while ignoring build output/scratch. Run it against the real corpus; fix any converter defects the real content surfaces (TDD); commit the artifacts.

**Tech Stack:** Python 3.12, MkDocs Material 9.5.42, pytest 8. Existing suite is 56 tests (must stay green).

## Global Constraints

- **Branch-only.** Work on `feat/claat-migration-toolkit`; commit only there. No PR to main, no `repos.yaml` registration, no `mkdocs gh-deploy`/publish.
- Everything under `learn-site-content/migration/`. `workshop-markdown/` is READ-ONLY. Run commands from repo root `/home/ubuntu/workspace/dynatrace-codespaces/learn-site-content`.
- **The generated repos are branch-only review artifacts.** Committed repo *source* (docs, images, config) is tracked; built `site/` output and any scratch are NOT.
- Python as `python3`; pytest as `python3 -m pytest`; mkdocs as `python3 -m mkdocs`.
- **Registry is the single source of truth** for each workshop's `repo_name`, `title`, `tags`, `duration`, and selector — read it, don't re-hardcode.
- Existing toolkit signatures (do not change): `scaffold_repo(out_repo_dir, *, site_name, repo_url, template_dir, framework_dir)`; `convert_workshop(workshop, corpus_dir, out_repo_dir) -> dict`; `build_review(log, repo_dir) -> str`; `repos_yaml_snippet(log, repo_name, title, tags, duration) -> str`; `build_tracker(logs, orphans, out_dir) -> str`; `find_orphans(corpus_dir) -> list[str]`; `WORKSHOPS: list[Workshop]`.

---

### Task 1: `.gitignore` — track generated repo source, ignore build output & scratch

**Files:**
- Modify: `.gitignore`

**Interfaces:** none (config only).

- [ ] **Step 1: Write a failing check (documents intent)**

Run these and note current (wrong) behavior — with the blanket `migration/out/` ignore, a repo source file is currently ignored:
```bash
git check-ignore -q migration/out/enablement-demo/docs/index.md && echo "IGNORED (wrong)" || echo "tracked (want this)"
```
Expected now: `IGNORED (wrong)`

- [ ] **Step 2: Replace the blanket ignore in `.gitignore`**

Find this block:
```text
# CLaaT migration generated repos (branch-only artifacts, do not commit)
migration/out/
```
Replace it with:
```text
# CLaaT migration: commit generated repo SOURCE for review; never commit build output or scratch
migration/out/**/site/
migration/out/_*
```

- [ ] **Step 3: Verify the new ignore semantics**

Run:
```bash
git check-ignore -q migration/out/enablement-demo/docs/index.md && echo "A:IGNORED" || echo "A:tracked"
git check-ignore -q migration/out/enablement-demo/site/index.html && echo "B:IGNORED" || echo "B:tracked"
git check-ignore -q migration/out/_grail-src && echo "C:IGNORED" || echo "C:tracked"
```
Expected: `A:tracked`, `B:IGNORED`, `C:IGNORED`

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore(migration): track generated repo source, ignore build output and scratch"
```

---

### Task 2: `migration/fanout.py` driver

**Files:**
- Create: `migration/fanout.py`
- Test: `migration/tests/test_fanout.py`

**Interfaces:**
- Consumes: `WORKSHOPS`/`find_orphans` (registry), `scaffold_repo`, `convert_workshop`, `build_review`/`repos_yaml_snippet`, `build_tracker`.
- Produces:
  - `run_fanout(workshops, corpus_dir, out_dir, *, build=True, template_dir="../enablement-codespaces-template", framework_dir="../codespaces-framework") -> list[dict]` — for each workshop: scaffold `out_dir/<repo_name>`, convert, write REVIEW.md + REVIEW-repos-snippet.yaml, and (if `build`) run `mkdocs build --strict`. After all, write the tracker. Returns one result dict per workshop: `{"workshop", "repo", "labs", "build_ok": bool|None, "build_output": str}`.
  - `main(argv)` CLI: `--out <dir> [--corpus workshop-markdown] [--no-build] [--only <name>]`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_fanout.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_fanout.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.fanout'`

- [ ] **Step 3: Write `migration/fanout.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_fanout.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Run the whole suite**

Run: `python3 -m pytest migration/tests/ -q`
Expected: `57 passed`

- [ ] **Step 6: Commit**

```bash
git add migration/fanout.py migration/tests/test_fanout.py
git commit -m "feat(migration): fanout.py driver (scaffold+convert+review+strict-build per workshop)"
```

---

### Task 3: Execute the fan-out on the real corpus (gate on strict build)

**Files:**
- Generated (git-ignored build output; committed source handled in Task 4): `migration/out/*`
- Possibly Modify (only if the real content surfaces a converter defect): `migration/claat/*.py` / `migration/convert.py` + a new regression test under `migration/tests/`.

**Interfaces:** consumes `migration/fanout.py` (Task 2).

- [ ] **Step 1: Ensure MkDocs Material is installed (framework-pinned)**

Run:
```bash
python3 -m pip install --quiet -r enablement-codespaces-template/docs/requirements/requirements-mkdocs.txt
python3 -m mkdocs --version
```
Expected: prints a mkdocs version (Material 9.5.42 installed).

- [ ] **Step 2: Clean any prior output and run the full fan-out**

Run:
```bash
rm -rf migration/out
python3 -m migration.fanout --out migration/out --corpus workshop-markdown
```
Expected: one line per workshop. **All 7 must print `[OK]`:** `enablement-azure-grail`, `enablement-azure-aks-levelup`, `enablement-azure-gen2`, `enablement-aws-immersion-day`, `enablement-aws-immersion-day-saas`, `enablement-aws-serverless`, `enablement-aws-selfpaced`. Exit code 0.

- [ ] **Step 3: If any workshop printed `[FAIL]` — diagnose, fix the converter via TDD, re-run**

A strict-build failure is a real converter finding on real content (likely culprits: an unescaped character in a page title or nav, a broken/relative link mkdocs rejects, a duplicate slug, or a missing image). For each distinct failure:
1. Read the printed `build_output` to find the offending file/line in `migration/out/<repo>/docs/`.
2. Reproduce the root cause as a **failing unit test** under `migration/tests/` against the responsible transform (e.g. a title/link/slug case in `test_document.py`, `test_convert_cli.py`, or `test_links.py`). Confirm it FAILS.
3. Fix the responsible module in `migration/` minimally and generally (never hand-edit the generated `migration/out/` — it is regenerated). Confirm the test PASSES and `python3 -m pytest migration/tests/ -q` stays green.
4. Commit the fix: `git add migration/<file> migration/tests/<test> && git commit -m "fix(migration): <what> surfaced by <workshop> strict build"`.
5. Re-run Step 2 (or `--only <workshop>` for the affected one) and confirm `[OK]`.
Repeat until all 7 are `[OK]`.

- [ ] **Step 4: Record the fan-out result summary**

Run:
```bash
echo "=== tracker ===" && sed -n '1,40p' migration/out/MIGRATION-TRACKER.md
echo "=== per-repo page counts ===" && for r in migration/out/enablement-*; do echo "$(basename "$r"): $(ls "$r"/docs/*.md | wc -l) pages"; done
```
Expected: the tracker table lists all 7 repos with flag counts, `TODO` assignees, and the `## Unassigned labs` section shows `aws-dt-lab0-Prereq`. Each repo has `index.md` + one page per selected lab.

- [ ] **Step 5: Confirm every generated site is strict-clean (final gate)**

Run:
```bash
for r in migration/out/enablement-*; do
  (cd "$r" && python3 -m mkdocs build --strict >/dev/null 2>&1 && echo "OK  $(basename "$r")" || echo "FAIL $(basename "$r")")
done
```
Expected: `OK` for all 7. (No commit in this task beyond any converter fixes from Step 3 — the generated artifacts are committed in Task 4.)

---

### Task 4: Commit generated content + tracker to the branch

**Files:**
- Add (generated repo source under): `migration/out/enablement-*/**` (docs, img, config) and `migration/out/MIGRATION-TRACKER.md`

**Interfaces:** none (operational commit).

- [ ] **Step 1: Confirm the ignore rules keep build output out**

Run:
```bash
git status --porcelain migration/out | grep -c '/site/' || echo "0 site files staged-or-untracked (good)"
git check-ignore -q migration/out/enablement-azure-grail/site && echo "site ignored (good)" || echo "WARN site not ignored"
```
Expected: no `site/` paths appear; `site ignored (good)`.

- [ ] **Step 2: Stage the generated repo source and the tracker**

Run:
```bash
git add migration/out
git status --short | head -20
echo "--- total files staged ---"; git diff --cached --numstat | wc -l
```
Expected: many files staged under `migration/out/enablement-*/` (docs, images, config) plus `migration/out/MIGRATION-TRACKER.md`; NO `site/` paths. (Volume is large — AWS repos duplicate shared-lab images by design; this is expected for a review branch.)

- [ ] **Step 3: Commit**

```bash
git commit -m "content(migration): generate 7 workshop repos for teammate review

Fan-out of the CLaaT corpus into Codespaces-framework repos (grail, azure-aks-levelup,
azure-gen2, aws-immersion-day, aws-immersion-day-saas, aws-serverless, aws-selfpaced).
Each passes mkdocs build --strict. See migration/out/MIGRATION-TRACKER.md for the
assignment map and each repo's REVIEW.md for the per-repo checklist. Branch-only."
```

- [ ] **Step 4: Report the committed footprint**

Run:
```bash
git show --stat HEAD | tail -5
echo "=== repos on branch ===" && ls -d migration/out/enablement-*
```
Expected: the commit records the generated files; 7 `enablement-*` repos present.

---

## Self-Review notes (author check against spec §4–5)

- **§4 fan-out targets (7 repos):** Task 3 Step 2 runs all 7 via the registry-driven driver; Step 5 gates each on strict build. **Covered.**
- **§4 per-repo strict-build gate + converter-fix discipline:** Task 3 Step 3 (TDD fix loop). **Covered.**
- **§4 orphan guard surfaces `aws-dt-lab0-Prereq`:** Task 3 Step 4 verifies the tracker's Unassigned section. **Covered.**
- **§5 single review branch, out/ committed (source only):** Task 1 (gitignore: track source, ignore `site/`+scratch); Task 4 (commit). **Covered.**
- **§5 MIGRATION-TRACKER as the map:** built by the driver (Task 2/3), committed (Task 4). **Covered.**
- **§5 no PR/main/publish:** all commits on `feat/claat-migration-toolkit`; no gh-deploy/registration step anywhere. The `content-review` handoff branch is created by the controller after this plan (finishing step), not here. **Covered.**
- **Placeholder scan:** the only `TODO` strings are the tracker's Assignee column values (intended output). No plan gaps.
- **Type consistency:** `run_fanout` result keys (`workshop/repo/labs/build_ok/build_output`) used consistently in `main`; driver calls match the frozen toolkit signatures in Global Constraints. Suite 56→57 (one driver test). **OK.**
