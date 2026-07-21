# CLaaT Toolkit Hardening Implementation Plan (Plan 1 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the existing `migration/` CLaaT→MkDocs toolkit with a declarative view/workshop registry (dir_glob + tag selectors), CLaaT `id` capture, a cloud-prose heuristic flag, a MIGRATION-TRACKER generator, and two cosmetic cleanups — so the fan-out (Plan 2) can run one repo per workshop.

**Architecture:** Add a `migration/registry.py` (workshop definitions + lab selection over the whole corpus) and a `migration/claat/cloudprose.py` (rule-14 scan). Refactor `migration/convert.py` from directory-based `convert_family` to registry-driven `convert_workshop`. Extend `migration/review.py` (id in context, env section) and add `migration/tracker.py` (cross-repo aggregate).

**Tech Stack:** Python 3.12, PyYAML 6, pytest 8. All existing 40 tests must stay green.

## Global Constraints

- **Branch-only.** Work on `feat/claat-migration-toolkit`; commit only there. No PR to main, no `repos.yaml` registration, no publish.
- Everything under `learn-site-content/migration/`. `workshop-markdown/` is READ-ONLY. Run commands from the repo root `/home/ubuntu/workspace/dynatrace-codespaces/learn-site-content`.
- **Admonition/flag conventions unchanged:** flag `section` values are `blocking`, `env`, `screenshot`, `alt`, `judgment`.
- **Excluded from all selection:** directories ending `-jp`, directories starting `redhat101-`, and the `Unused` directory (it has no top-level `README.md`, but exclude by name too).
- **Tag matching normalizes whitespace:** split the `tags` header on `,` and `.strip()` each element before comparing.
- Python invoked as `python3`; pytest as `python3 -m pytest`.

---

### Task 1: Cosmetic cleanups (dead code from pilot final review)

**Files:**
- Modify: `migration/convert.py` (remove unused `from dataclasses import asdict`)
- Modify: `migration/scaffold.py` (remove unused `_KEEP_DOCS_DIRS` constant)

**Interfaces:**
- Consumes: nothing. Produces: nothing new — pure deletions.

- [ ] **Step 1: Confirm both symbols are unused**

Run: `grep -n "asdict" migration/convert.py; echo "---"; grep -n "_KEEP_DOCS_DIRS" migration/scaffold.py`
Expected: `asdict` appears only on the import line (the code uses `asdict_flag`, a different name); `_KEEP_DOCS_DIRS` appears only on its definition line.

- [ ] **Step 2: Remove the dead import in `migration/convert.py`**

Delete this line (near the top of the file):
```python
from dataclasses import asdict
```

- [ ] **Step 3: Remove the dead constant in `migration/scaffold.py`**

Delete this line:
```python
_KEEP_DOCS_DIRS = {"overrides", "snippets", "requirements", "stylesheets", "img"}
```

- [ ] **Step 4: Run the whole suite to confirm no regression**

Run: `python3 -m pytest migration/tests/ -q`
Expected: `40 passed`

- [ ] **Step 5: Commit**

```bash
git add migration/convert.py migration/scaffold.py
git commit -m "chore(migration): remove dead asdict import and _KEEP_DOCS_DIRS constant"
```

---

### Task 2: Tag parsing + view/workshop registry

**Files:**
- Create: `migration/registry.py`
- Test: `migration/tests/test_registry.py`

**Interfaces:**
- Consumes: `migration.claat.header.parse_header`, `migration.claat.slugify.natural_key`.
- Produces:
  - `parse_tags(meta: dict) -> list[str]` — split `meta["tags"]` on `,`, strip each, drop empties.
  - `Workshop` dataclass: `name: str, repo_name: str, title: str, selector_type: str ("dir_glob"|"tag"), selector: str, tags: list[str], duration: str`.
  - `WORKSHOPS: list[Workshop]` — the registry (Grail + fan-out targets).
  - `get_workshop(name: str) -> Workshop` — lookup by `name`, raises `KeyError` if absent.
  - `is_excluded(dirname: str) -> bool` — True for `-jp`, `redhat101-*`, `Unused`.
  - `select_labs(workshop: Workshop, corpus_dir) -> list[pathlib.Path]` — scan corpus, return matching lab dirs ordered by `natural_key(dir.name)`.
  - `find_orphans(corpus_dir) -> list[str]` — active, non-excluded lab dir names claimed by NO workshop.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_registry.py`

```python
import pathlib

from migration.registry import (
    parse_tags, get_workshop, is_excluded, select_labs, find_orphans, WORKSHOPS,
)

CORPUS = pathlib.Path("/home/ubuntu/workspace/dynatrace-codespaces/learn-site-content/workshop-markdown")


def test_parse_tags_strips_whitespace_and_empties():
    assert parse_tags({"tags": "aws-immersion-day-saas ,  modernization,"}) == [
        "aws-immersion-day-saas", "modernization",
    ]


def test_parse_tags_missing_key():
    assert parse_tags({}) == []


def test_is_excluded():
    assert is_excluded("aws-lab1-jp")
    assert is_excluded("redhat101-lab0")
    assert is_excluded("Unused")
    assert not is_excluded("aws-lab1")


def test_get_workshop_known_and_unknown():
    w = get_workshop("azure-aks-levelup")
    assert w.selector_type == "dir_glob"
    assert w.selector == "azure-aks-levelup-lab*"
    import pytest
    with pytest.raises(KeyError):
        get_workshop("does-not-exist")


def test_select_labs_dir_glob_orders_naturally():
    w = get_workshop("azure-gen2")
    labs = [p.name for p in select_labs(w, CORPUS)]
    # azure-lab* only — must not pull grail or aks-levelup
    assert all(n.startswith("azure-lab") for n in labs)
    assert not any("grail" in n or "aks-levelup" in n for n in labs)
    assert len(labs) >= 8


def test_select_labs_by_tag_includes_shared_lab():
    w = get_workshop("aws-serverless")  # tag aws-immersion-day-serverless
    names = [p.name for p in select_labs(w, CORPUS)]
    # aws-lab6 is tagged for serverless (among others) and must appear
    assert "aws-lab6" in names
    # a saas-only lab must NOT appear
    assert "aws-lab0 SAAS" not in names


def test_select_labs_excludes_jp_and_openshift():
    for w in WORKSHOPS:
        names = [p.name for p in select_labs(w, CORPUS)]
        assert not any(n.endswith("-jp") or n.startswith("redhat101-") for n in names)


def test_find_orphans_reports_prereq():
    orphans = find_orphans(CORPUS)
    # aws-dt-lab0-Prereq (tag Dynatrace-SAAS-Prereq) matches no workshop selector
    assert "aws-dt-lab0-Prereq" in orphans
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_registry.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.registry'`

- [ ] **Step 3: Write `migration/registry.py`**

```python
import fnmatch
import pathlib
from dataclasses import dataclass, field

from migration.claat.header import parse_header
from migration.claat.slugify import natural_key


def parse_tags(meta: dict) -> list[str]:
    return [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]


@dataclass
class Workshop:
    name: str
    repo_name: str
    title: str
    selector_type: str  # "dir_glob" | "tag"
    selector: str
    tags: list[str] = field(default_factory=list)
    duration: str = "TBD"


WORKSHOPS: list[Workshop] = [
    Workshop("azure-grail", "enablement-azure-grail", "Azure Grail",
             "dir_glob", "azure-grail-lab*", ["azure", "grail", "kubernetes"], "2h"),
    Workshop("azure-aks-levelup", "enablement-azure-aks-levelup", "Azure AKS LevelUp",
             "dir_glob", "azure-aks-levelup-lab*", ["azure", "aks", "kubernetes"], "1.5h"),
    Workshop("azure-gen2", "enablement-azure-gen2", "Azure Gen2",
             "dir_glob", "azure-lab*", ["azure", "modernization"], "3h"),
    Workshop("aws-immersion-day", "enablement-aws-immersion-day", "AWS Immersion Day",
             "tag", "aws-immersion-day", ["aws"], "3h"),
    Workshop("aws-immersion-day-saas", "enablement-aws-immersion-day-saas",
             "AWS Immersion Day (SaaS)", "tag", "aws-immersion-day-saas", ["aws"], "3h"),
    Workshop("aws-serverless", "enablement-aws-serverless", "AWS Serverless Observability",
             "tag", "aws-immersion-day-serverless", ["aws", "serverless"], "1.5h"),
    Workshop("aws-selfpaced", "enablement-aws-selfpaced", "AWS Self-paced",
             "tag", "aws-selfpaced", ["aws"], "3h"),
]

_BY_NAME = {w.name: w for w in WORKSHOPS}


def get_workshop(name: str) -> Workshop:
    return _BY_NAME[name]


def is_excluded(dirname: str) -> bool:
    return dirname.endswith("-jp") or dirname.startswith("redhat101-") or dirname == "Unused"


def _lab_dirs(corpus_dir: pathlib.Path):
    for d in sorted(corpus_dir.iterdir(), key=lambda p: natural_key(p.name)):
        if not d.is_dir():
            continue
        if is_excluded(d.name):
            continue
        if not (d / "README.md").exists():
            continue
        yield d


def _matches(workshop: Workshop, d: pathlib.Path) -> bool:
    if workshop.selector_type == "dir_glob":
        return fnmatch.fnmatch(d.name, workshop.selector)
    meta, _ = parse_header((d / "README.md").read_text())
    return workshop.selector in parse_tags(meta)


def select_labs(workshop: Workshop, corpus_dir) -> list[pathlib.Path]:
    corpus_dir = pathlib.Path(corpus_dir)
    return [d for d in _lab_dirs(corpus_dir) if _matches(workshop, d)]


def find_orphans(corpus_dir) -> list[str]:
    corpus_dir = pathlib.Path(corpus_dir)
    claimed = set()
    for w in WORKSHOPS:
        claimed.update(d.name for d in select_labs(w, corpus_dir))
    return [d.name for d in _lab_dirs(corpus_dir) if d.name not in claimed]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_registry.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Run the whole suite**

Run: `python3 -m pytest migration/tests/ -q`
Expected: `48 passed`

- [ ] **Step 6: Commit**

```bash
git add migration/registry.py migration/tests/test_registry.py
git commit -m "feat(migration): view/workshop registry with dir_glob and tag selectors"
```

---

### Task 3: Cloud-prose heuristic scanner (spec rule 14)

**Files:**
- Create: `migration/claat/cloudprose.py`
- Test: `migration/tests/test_cloudprose.py`

**Interfaces:**
- Consumes: `migration.claat.models.Flag`.
- Produces: `scan_cloud_prose(markdown: str) -> Flag | None` — returns ONE `env`-section Flag if the text contains any cloud-account/portal keyword (case-insensitive), else `None`. Keywords: `azure portal`, `aws console`, `azure pass`, `promo code`, `subscription`, `credentials`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_cloudprose.py`

```python
from migration.claat.cloudprose import scan_cloud_prose


def test_flags_azure_portal_case_insensitive():
    f = scan_cloud_prose("Open the Azure PORTAL and search for the cluster.")
    assert f is not None
    assert f.section == "env"


def test_flags_promo_code():
    f = scan_cloud_prose("You will receive an Azure Pass promo code from staff.")
    assert f is not None


def test_no_flag_when_absent():
    assert scan_cloud_prose("Deploy the operator with kubectl and observe traces.") is None


def test_message_mentions_docs_first():
    f = scan_cloud_prose("Log in with your subscription credentials.")
    assert "docs-first" in f.message.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_cloudprose.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.cloudprose'`

- [ ] **Step 3: Write `migration/claat/cloudprose.py`**

```python
from migration.claat.models import Flag

_KEYWORDS = (
    "azure portal", "aws console", "azure pass",
    "promo code", "subscription", "credentials",
)


def scan_cloud_prose(markdown: str) -> "Flag | None":
    low = markdown.lower()
    hit = next((k for k in _KEYWORDS if k in low), None)
    if hit is None:
        return None
    return Flag(
        section="env",
        message=f"References a cloud account/portal ('{hit}'); "
        "confirm docs-first wording (learner uses their own account).",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_cloudprose.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/cloudprose.py migration/tests/test_cloudprose.py
git commit -m "feat(migration): cloud-prose heuristic env flag (spec rule 14)"
```

---

### Task 4: Registry-driven `convert_workshop` (+ id capture, cloud-prose)

**Files:**
- Modify: `migration/convert.py` (replace `convert_family`/`_lab_dirs` with `convert_workshop`/`_convert_lab`; update CLI)
- Modify: `migration/tests/test_convert_cli.py` (retarget to `convert_workshop`)
- Modify: `migration/README.md` (update the `convert` invocation example)

**Interfaces:**
- Consumes: `migration.claat.document.convert_document`, `migration.claat.slugify.slug_text`, `migration.registry.Workshop`/`get_workshop`/`select_labs`, `migration.claat.cloudprose.scan_cloud_prose`.
- Produces:
  - `convert_workshop(workshop: Workshop, corpus_dir, out_repo_dir) -> dict` — selects labs via `select_labs`, writes `docs/<n>-<labslug>.md`, copies images to `docs/img/<labslug>/`, injects nav (Welcome first), writes `transform_log.json`. Each lab log entry gains `"id"` (from `doc.metadata`). Per lab, flags include the cloud-prose `env` flag (when present), plus the existing `screenshot` and `judgment` flags.
  - `main(argv)` CLI: `--workshop <name> --out <dir> [--corpus workshop-markdown]`.
- `labslug = slug_text(dir_name)` (no strip-prefix; dir names are already workshop-scoped).

- [ ] **Step 1: Rewrite the test** — replace the entire contents of `migration/tests/test_convert_cli.py`

```python
import json
import pathlib

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_convert_cli.py -v`
Expected: FAIL — `ImportError: cannot import name 'convert_workshop' from 'migration.convert'`

- [ ] **Step 3: Rewrite `migration/convert.py`**

```python
import argparse
import json
import pathlib
import shutil
import sys

from migration.claat.cloudprose import scan_cloud_prose
from migration.claat.document import convert_document
from migration.claat.slugify import slug_text
from migration.registry import Workshop, get_workshop, select_labs


def asdict_flag(f) -> dict:
    return {"section": f.section, "message": f.message, "locator": f.locator, "line": f.line}


def _convert_lab(lab_dir: pathlib.Path, index: int, docs: pathlib.Path) -> tuple[dict, str]:
    name = lab_dir.name
    labslug = slug_text(name)
    doc = convert_document((lab_dir / "README.md").read_text(), lab_dir / "img", labslug)
    page = f"{index}-{labslug}.md"
    (docs / page).write_text(doc.markdown)

    img_out = docs / "img" / labslug
    img_out.mkdir(parents=True, exist_ok=True)
    for orig, new in doc.image_renames.items():
        src_img = lab_dir / "img" / orig
        if src_img.exists():
            shutil.copyfile(src_img, img_out / new)

    flags = [asdict_flag(f) for f in doc.flags]
    env_flag = scan_cloud_prose(doc.markdown)
    if env_flag is not None:
        flags.append(asdict_flag(env_flag))
    flags.append({"section": "screenshot", "message":
                  f"Run this lab and verify its {len(doc.image_renames)} "
                  f"screenshots are current (technical-accuracy gate).",
                  "locator": "", "line": 0})
    flags.append({"section": "judgment", "message":
                  "Confirm this lab still belongs in the migrated workshop.",
                  "locator": "", "line": 0})

    lab_log = {
        "labslug": labslug, "source": name, "page": f"docs/{page}",
        "id": doc.metadata.get("id", ""),
        "title": doc.title, "total_minutes": doc.total_minutes,
        "image_count": len(doc.image_renames), "flags": flags,
        "metadata": doc.metadata,
    }
    safe_title = doc.title.replace("\\", "\\\\").replace('"', '\\"')
    nav_line = f'  - "{index}. {safe_title}": {page}'
    return lab_log, nav_line


def convert_workshop(workshop: Workshop, corpus_dir, out_repo_dir) -> dict:
    out_repo_dir = pathlib.Path(out_repo_dir)
    docs = out_repo_dir / "docs"
    labs_log = []
    nav_lines = ['  - "Welcome": index.md']

    for i, lab_dir in enumerate(select_labs(workshop, corpus_dir), start=1):
        lab_log, nav_line = _convert_lab(lab_dir, i, docs)
        labs_log.append(lab_log)
        nav_lines.append(nav_line)

    mk = out_repo_dir / "mkdocs.yaml"
    mk.write_text(mk.read_text().replace("# NAV_PLACEHOLDER", "\n".join(nav_lines)))

    log = {"repo": out_repo_dir.name, "workshop": workshop.name, "labs": labs_log}
    (out_repo_dir / "transform_log.json").write_text(json.dumps(log, indent=2))
    return log


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Convert a CLaaT workshop by registry name.")
    ap.add_argument("--workshop", required=True, help="registry workshop name")
    ap.add_argument("--out", required=True, help="output repo dir (already scaffolded)")
    ap.add_argument("--corpus", default="workshop-markdown")
    args = ap.parse_args(argv)
    log = convert_workshop(get_workshop(args.workshop), args.corpus, args.out)
    print(f"Converted {len(log['labs'])} labs into {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the retargeted test to verify it passes**

Run: `python3 -m pytest migration/tests/test_convert_cli.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Run the whole suite**

Run: `python3 -m pytest migration/tests/ -q`
Expected: `50 passed`

- [ ] **Step 6: Update the `convert` example in `migration/README.md`**

Find the old convert invocation line (it uses positional args + `--strip-prefix`, e.g. `python3 -m migration.convert migration/out/_grail-src ... --strip-prefix ...`) and any `_grail-src` symlink setup lines, and replace that convert step with the registry-driven form:
```markdown
    # 2. scaffold -> convert (by registry workshop name) -> review
    python3 -m migration.scaffold migration/out/enablement-azure-grail \
      --site-name "Dynatrace Enablement Lab: Azure Grail" \
      --repo-url "https://github.com/dynatrace-wwse/enablement-azure-grail"
    python3 -m migration.convert --workshop azure-grail --out migration/out/enablement-azure-grail
    python3 -m migration.review migration/out/enablement-azure-grail \
      --title "Azure Grail" --tags "azure,grail,kubernetes" --duration "2h"
```
Delete the `mkdir -p migration/out/_grail-src` / `ln -s ...` lines — the symlink workaround is gone (convert now scans `workshop-markdown/` directly).

- [ ] **Step 7: Commit**

```bash
git add migration/convert.py migration/tests/test_convert_cli.py migration/README.md
git commit -m "feat(migration): registry-driven convert_workshop with id capture and env flag"
```

---

### Task 5: REVIEW.md — id in context + env section

**Files:**
- Modify: `migration/review.py` (add `id` to §0 lab map; add `env` section; renumber sections)
- Modify: `migration/tests/test_review.py` (assert new section + id)

**Interfaces:**
- Consumes: the `transform_log.json` schema, now with `lab["id"]` and flags of section `env`.
- Produces: `build_review` output whose section order is: `## 0. Context`, `## 1. Blocking`, `## 2. Environment (cloud-account prose)`, `## 3. Run & re-capture`, `## 4. Alt-text review`, `## 5. Judgment calls`, `## 6. Definition of done`. The §0 lab map line includes the source `id`. `repos_yaml_snippet` unchanged.

- [ ] **Step 1: Update the test** — replace the two section-list assertions in `migration/tests/test_review.py`

Add `"id": "sample-lab-id"` to the single lab dict in the `LOG` fixture, add one env flag to that lab's `flags` list:
```python
            {"section": "env", "message": "References a cloud account", "locator": "", "line": 0},
```
Then replace `test_build_review_has_all_sections` with:
```python
def test_build_review_has_all_sections(tmp_path):
    md = build_review(LOG, tmp_path)
    assert "## 1. Blocking" in md
    assert "## 2. Environment" in md
    assert "## 3. Run & re-capture" in md
    assert "## 4. Alt-text review" in md
    assert "## 5. Judgment calls" in md
    assert "## 6. Definition of done" in md
    assert (tmp_path / "REVIEW.md").exists()


def test_context_map_includes_source_id(tmp_path):
    md = build_review(LOG, tmp_path)
    assert "sample-lab-id" in md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_review.py -v`
Expected: FAIL — `## 2. Environment` not found (and `sample-lab-id` not found).

- [ ] **Step 3: Edit `migration/review.py`** — replace the `_SECTION_TITLES`/`_ORDER` block and the §0 map loop and the Definition-of-done block

Replace `_SECTION_TITLES` and `_ORDER` with:
```python
_SECTION_TITLES = {
    "blocking": "## 1. Blocking — must resolve before committing the branch",
    "env": "## 2. Environment (cloud-account prose) — confirm docs-first wording",
    "screenshot": "## 3. Run & re-capture (validates technical accuracy)",
    "alt": "## 4. Alt-text review (batch-approvable)",
    "judgment": "## 5. Judgment calls (does this lab still belong?)",
}
_ORDER = ["blocking", "env", "screenshot", "alt", "judgment"]
```

Replace the §0 lab-map loop:
```python
    for lab in log["labs"]:
        lines.append(f"    - {lab['source']} → {lab['page']} "
                     f"(id: {lab.get('id', '?')}, {lab['image_count']} images)")
```

Replace the Definition-of-done header from `## 5.` to `## 6.`:
```python
        "## 6. Definition of done",
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_review.py -v`
Expected: PASS (all in file)

- [ ] **Step 5: Run the whole suite**

Run: `python3 -m pytest migration/tests/ -q`
Expected: `50 passed`

- [ ] **Step 6: Commit**

```bash
git add migration/review.py migration/tests/test_review.py
git commit -m "feat(migration): REVIEW.md env section and source id in context map"
```

---

### Task 6: MIGRATION-TRACKER.md generator

**Files:**
- Create: `migration/tracker.py`
- Test: `migration/tests/test_tracker.py`

**Interfaces:**
- Consumes: a list of `transform_log.json` dicts (each with `repo`, `workshop`, `labs[]` where each lab has `flags[]`), and `migration.registry.find_orphans`.
- Produces:
  - `build_tracker(logs: list[dict], orphans: list[str], out_dir) -> str` — writes `<out_dir>/MIGRATION-TRACKER.md`: a table with columns `Workshop | Repo | Labs | Blocking | Env | Screenshot | Alt | Judgment | Assignee | Status`, one row per log (Assignee=`TODO`, Status=`not started`), then an `## Unassigned labs` section listing `orphans` (or "none").
  - `main(argv)` CLI: `--out <dir>` scans `<out>/*/transform_log.json`, computes orphans from `--corpus`, writes the tracker.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_tracker.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_tracker.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.tracker'`

- [ ] **Step 3: Write `migration/tracker.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_tracker.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run the whole suite**

Run: `python3 -m pytest migration/tests/ -q`
Expected: `53 passed`

- [ ] **Step 6: Commit**

```bash
git add migration/tracker.py migration/tests/test_tracker.py
git commit -m "feat(migration): MIGRATION-TRACKER.md generator with orphan reporting"
```

---

## Self-Review notes (author check against spec §3)

- **§3.1 view registry** — Task 2 (`registry.py`: `Workshop`, `WORKSHOPS`, `dir_glob`+`tag` selectors, `select_labs` corpus scan, `find_orphans`); Task 4 consumes it (`convert_workshop`). Symlink workaround eliminated (convert scans corpus via `select_labs`). **Covered.**
- **§3.2 id capture** — Task 4 adds `lab["id"]` to the log; Task 5 surfaces it in REVIEW §0. **Covered.**
- **§3.3 cloud-prose flag** — Task 3 (`cloudprose.py`, `env` section, non-blocking); Task 4 appends it per lab; Task 5 renders the Environment section. **Covered.**
- **§3.4 MIGRATION-TRACKER** — Task 6 (`tracker.py`): per-repo counts, Assignee TODO, Status, orphan section. **Covered.**
- **§3.5 cosmetic cleanups** — Task 1 (dead `asdict`, `_KEEP_DOCS_DIRS`). **Covered.**
- **Excluded content** — `is_excluded` (Task 2) drops `-jp`, `redhat101-*`, `Unused`; every selector routes through `_lab_dirs`. **Covered.**
- **Placeholder scan** — the only literal `TODO`/`not started` strings are intentional column values in generated tracker output, and `@TODO` in the pre-existing repos.yaml snippet (unchanged). No plan gaps.
- **Type consistency** — `Workshop` field names identical across Tasks 2/4/6; `transform_log.json` gains `workshop` (written Task 4, read Task 6) and `id` (written Task 4, read Task 5); flag section `env` introduced Task 3, consumed Tasks 4/5/6 with the same string. Suite count rises 40→48→50→50→53 across tasks (each task states its expected total). **OK.**
