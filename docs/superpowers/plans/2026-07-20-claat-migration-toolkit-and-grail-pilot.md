# CLaaT Migration Toolkit + Azure Grail Pilot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the one-time `migration/` Python toolkit (`convert.py` + `scaffold.py` + `review.py`) that turns a CLaaT workshop family into a Codespaces-framework repo, and run it end-to-end on the Azure Grail pilot until `mkdocs build --strict` passes.

**Architecture:** A small package `migration/claat/` holds pure, independently-tested transform functions (header, asides, duration, links, lists, images) orchestrated by `document.convert_document()`. Three thin CLIs wrap them: `scaffold.py` (repo skeleton from the template), `convert.py` (family → `docs/*.md` + images + nav + `transform_log.json`), and `review.py` (`transform_log.json` → `REVIEW.md` + `repos.yaml` snippet + tracker row). The pilot generates `migration/out/enablement-azure-grail/` (a git-ignored artifact) and builds it locally.

**Tech Stack:** Python 3.12, PyYAML 6, pytest 8, MkDocs Material 9.5.42 (framework-pinned).

## Global Constraints

- **Branch-only delivery.** All commits go to branch `feat/claat-migration-toolkit` (create it off `main`). **No PR to `main`, no `repos.yaml` registration in the framework, no `mkdocs gh-deploy`/publishing.** The generated pilot repo stays a local artifact under `migration/out/` (git-ignored) until the owner lifts the hold.
- **Toolkit location:** everything lives under `learn-site-content/migration/`. Run all commands from the `learn-site-content` repo root.
- **Source is read-only.** Never modify anything under `workshop-markdown/`. The converter only reads it.
- **Out of scope (do not build for):** JP variants, RedHat/OpenShift 101, `Unused/` archived labs, live cloud provisioning.
- **Framework asset source (local):** `../codespaces-framework/mkdocs-base.yaml` and `../codespaces-framework/docs/stylesheets/extra.css`. **Template source (local):** `../enablement-codespaces-template/`.
- **Admonition mapping (verbatim):** `<aside class="positive">` → `!!! tip`; `<aside class="negative">` → `!!! warning`.
- **Flag sections (verbatim):** `blocking`, `screenshot`, `alt`, `judgment`.

---

### Task 1: Toolkit skeleton, shared models, slugify util, fixture

**Files:**
- Create: `migration/__init__.py` (empty)
- Create: `migration/claat/__init__.py` (empty)
- Create: `migration/claat/models.py`
- Create: `migration/claat/slugify.py`
- Create: `migration/requirements.txt`
- Create: `migration/tests/__init__.py` (empty)
- Create: `migration/tests/fixtures/sample_claat/README.md`
- Create: `migration/tests/test_slugify.py`
- Create: `.gitignore` append (git-ignore `migration/out/`)

**Interfaces:**
- Produces: `Flag(section: str, message: str, locator: str = "", line: int = 0)` dataclass; `slug_filename(name: str) -> str`; `slug_text(text: str) -> str`; `natural_key(s: str) -> list`.

- [ ] **Step 1: Write `migration/requirements.txt`**

```text
pyyaml==6.0.2
pytest==8.4.2
```

- [ ] **Step 2: Write the failing test** — `migration/tests/test_slugify.py`

```python
from migration.claat.slugify import slug_filename, slug_text, natural_key


def test_slug_filename_replaces_spaces():
    assert slug_filename("lab2-app copy.png") == "lab2-app-copy.png"


def test_slug_filename_strips_zero_width_space():
    # U+200B zero-width space seen in real Grail asset names
    assert slug_filename("lab2-step8-services​ copy.png") == "lab2-step8-services-copy.png"


def test_slug_filename_lowercases_extension_only():
    assert slug_filename("Lab0-Step4-ands.PNG") == "Lab0-Step4-ands.png"


def test_slug_filename_collapses_multiple_hyphens():
    assert slug_filename("a  --  b.gif") == "a-b.gif"


def test_slug_text_for_ids_and_dirs():
    assert slug_text("aws-lab4 role") == "aws-lab4-role"


def test_natural_key_orders_lab10_after_lab2():
    names = ["lab10", "lab2", "lab1"]
    assert sorted(names, key=natural_key) == ["lab1", "lab2", "lab10"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /home/ubuntu/workspace/dynatrace-codespaces/learn-site-content && python3 -m pytest migration/tests/test_slugify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.slugify'`

- [ ] **Step 4: Write `migration/claat/slugify.py`**

```python
import re


def slug_filename(name: str) -> str:
    """Normalize an image filename: fix spaces/zero-width/invalid chars in the
    stem, keep case in the stem, lowercase the extension."""
    dot = name.rfind(".")
    stem, ext = (name[:dot], name[dot + 1:]) if dot > 0 else (name, "")
    stem = stem.replace("​", "")           # drop zero-width spaces
    stem = re.sub(r"[^A-Za-z0-9.-]+", "-", stem)  # any run of other chars -> hyphen
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return f"{stem}.{ext.lower()}" if ext else stem


def slug_text(text: str) -> str:
    """Slugify an id/directory name to lowercase hyphen form."""
    out = re.sub(r"[^A-Za-z0-9]+", "-", text.strip()).strip("-").lower()
    return out


def natural_key(s: str) -> list:
    """Sort key so 'lab2' < 'lab10'."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]
```

- [ ] **Step 5: Write `migration/claat/models.py`**

```python
from dataclasses import dataclass


@dataclass
class Flag:
    section: str        # one of: blocking, screenshot, alt, judgment
    message: str
    locator: str = ""   # substring to locate in final markdown (for line resolution)
    line: int = 0
```

- [ ] **Step 6: Write the fixture** — `migration/tests/fixtures/sample_claat/README.md`

```markdown
summary: Sample fixture codelab
id: sample-lab
categories: all,demo
tags: demo, sample
status: Published
authors: Test Author
Feedback Link: https://github.com/dt-alliances-workshops/workshops-content

# Sample Fixture Lab - One Of Each

## First Step
Duration: 3

Intro text with a <a href="https://example.com/" target="_blank">link</a>.

<aside class="positive">A single-line positive note.</aside>

1. Numbered item one
     ![image](img/pic one.png)
2. Numbered item two

## Second Step
Duration: 5

<aside class="negative">
A multi-paragraph warning.

It has two paragraphs and an image ![image](img/second.png).
</aside>

See [broken]( ) link.
```

- [ ] **Step 7: Create the fixture image files (empty placeholders) and package inits**

Run:
```bash
cd /home/ubuntu/workspace/dynatrace-codespaces/learn-site-content
mkdir -p migration/claat migration/tests/fixtures/sample_claat/img
touch migration/__init__.py migration/claat/__init__.py migration/tests/__init__.py
touch "migration/tests/fixtures/sample_claat/img/pic one.png" migration/tests/fixtures/sample_claat/img/second.png
```
Expected: files created, no output.

- [ ] **Step 8: Git-ignore the output dir** — append to `.gitignore`

```text

# CLaaT migration generated repos (branch-only artifacts, do not commit)
migration/out/
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_slugify.py -v`
Expected: PASS (6 passed)

- [ ] **Step 10: Commit**

```bash
git checkout -b feat/claat-migration-toolkit
git add migration/ .gitignore
git commit -m "feat(migration): toolkit skeleton, models, slugify util, fixture"
```

---

### Task 2: Header parser

**Files:**
- Create: `migration/claat/header.py`
- Test: `migration/tests/test_header.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `parse_header(text: str) -> tuple[dict[str, str], str]` — returns `(metadata, body)`. Metadata keys are lowercased with spaces→underscore (`Feedback Link` → `feedback_link`). `body` is everything after the header block (leading blank lines stripped).

- [ ] **Step 1: Write the failing test** — `migration/tests/test_header.py`

```python
from migration.claat.header import parse_header


HEADER = (
    "summary: Dynatrace Workshop on Azure Grail Introduction\n"
    "id: azure-grail-lab0\n"
    "categories: modernization,kubernetes,grail,all\n"
    "tags: azure, grail\n"
    "status: Published\n"
    "authors: Jay Gurbani\n"
    "Feedback Link: https://example.com/fb\n"
    "\n"
    "# Azure Grail Workshop Lab 0 - Setup\n"
    "\n"
    "Body starts here.\n"
)


def test_parse_header_extracts_all_keys():
    meta, body = parse_header(HEADER)
    assert meta["id"] == "azure-grail-lab0"
    assert meta["summary"] == "Dynatrace Workshop on Azure Grail Introduction"
    assert meta["feedback_link"] == "https://example.com/fb"


def test_parse_header_body_excludes_header():
    meta, body = parse_header(HEADER)
    assert body.startswith("# Azure Grail Workshop Lab 0 - Setup")
    assert "summary:" not in body


def test_parse_header_does_not_consume_duration_lines():
    # A body 'Duration: 3' line must NOT be swallowed as a header key.
    text = "id: x\n\n# Title\n\n## Step\nDuration: 3\n\nText\n"
    meta, body = parse_header(text)
    assert "duration" not in meta
    assert "Duration: 3" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_header.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.header'`

- [ ] **Step 3: Write `migration/claat/header.py`**

```python
import re

_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z ]*):\s*(.*)$")


def parse_header(text: str) -> tuple[dict[str, str], str]:
    """Parse the leading bare `key: value` CLaaT header block.

    The block is the run of key:value lines at the very start of the file,
    terminated by the first blank line or the first line starting with '#'.
    """
    lines = text.splitlines()
    meta: dict[str, str] = {}
    i = 0
    for i, line in enumerate(lines):
        if line.strip() == "" or line.startswith("#"):
            break
        m = _KEY_RE.match(line)
        if not m:
            break
        key = m.group(1).strip().lower().replace(" ", "_")
        meta[key] = m.group(2).strip()
    else:
        i = len(lines)
    body = "\n".join(lines[i:]).lstrip("\n")
    return meta, body
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_header.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/header.py migration/tests/test_header.py
git commit -m "feat(migration): CLaaT bare key:value header parser"
```

---

### Task 3: Duration stripper

**Files:**
- Create: `migration/claat/duration.py`
- Test: `migration/tests/test_duration.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `strip_duration(body: str) -> tuple[str, int]` — replaces each `Duration: N` line with `<!-- Duration: N min -->` and returns `(new_body, total_minutes)`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_duration.py`

```python
from migration.claat.duration import strip_duration


def test_strip_duration_removes_visible_line_and_sums():
    body = "## A\nDuration: 3\n\ntext\n\n## B\nDuration: 5\n\nmore\n"
    out, total = strip_duration(body)
    assert total == 8
    assert "Duration: 3" not in out.replace("<!-- Duration: 3 min -->", "")
    assert "<!-- Duration: 3 min -->" in out
    assert "<!-- Duration: 5 min -->" in out


def test_strip_duration_no_durations():
    out, total = strip_duration("## A\n\ntext\n")
    assert total == 0
    assert out == "## A\n\ntext\n"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_duration.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.duration'`

- [ ] **Step 3: Write `migration/claat/duration.py`**

```python
import re

_DUR_RE = re.compile(r"^Duration:\s*(\d+)\s*$", re.MULTILINE)


def strip_duration(body: str) -> tuple[str, int]:
    total = 0

    def repl(m: "re.Match") -> str:
        nonlocal total
        n = int(m.group(1))
        total += n
        return f"<!-- Duration: {n} min -->"

    return _DUR_RE.sub(repl, body), total
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_duration.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/duration.py migration/tests/test_duration.py
git commit -m "feat(migration): strip Duration lines, sum total minutes"
```

---

### Task 4: Aside → admonition converter

**Files:**
- Create: `migration/claat/asides.py`
- Test: `migration/tests/test_asides.py`

**Interfaces:**
- Consumes: `Flag` from `migration.claat.models`.
- Produces: `convert_asides(body: str) -> tuple[str, list[Flag]]` — converts `<aside class="positive|negative">…</aside>` (single- and multi-line) to `!!! tip` / `!!! warning` with a 4-space-indented body; flags multi-paragraph, image-bearing, or nested asides with section `blocking`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_asides.py`

```python
from migration.claat.asides import convert_asides


def test_single_line_positive_becomes_tip():
    out, flags = convert_asides('<aside class="positive">Be careful here.</aside>')
    assert "!!! tip" in out
    assert "    Be careful here." in out
    assert flags == []


def test_negative_becomes_warning():
    out, flags = convert_asides('<aside class="negative">Danger.</aside>')
    assert "!!! warning" in out


def test_multiline_with_image_is_flagged():
    src = (
        '<aside class="positive">\n'
        "Para one.\n\n"
        "Para two with ![image](img/x.png).\n"
        "</aside>"
    )
    out, flags = convert_asides(src)
    assert "!!! tip" in out
    # body indented
    assert "    Para one." in out
    assert any(f.section == "blocking" for f in flags)


def test_body_text_preserved_for_line_location():
    out, flags = convert_asides('<aside class="negative">Signout first.</aside>')
    assert "Signout first." in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_asides.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.asides'`

- [ ] **Step 3: Write `migration/claat/asides.py`**

```python
import re

from migration.claat.models import Flag

_ASIDE_RE = re.compile(
    r'<aside\s+class="(positive|negative)"\s*>(.*?)</aside>',
    re.DOTALL,
)
_ADMONITION = {"positive": "tip", "negative": "warning"}


def convert_asides(body: str) -> tuple[str, list[Flag]]:
    flags: list[Flag] = []

    def repl(m: "re.Match") -> str:
        kind = _ADMONITION[m.group(1)]
        inner = m.group(2).strip("\n")
        # Indent every line by 4 spaces (blank lines stay blank).
        indented = "\n".join(
            ("    " + ln) if ln.strip() else "" for ln in inner.splitlines()
        )
        has_image = "![" in inner
        multi_para = "\n\n" in inner.strip()
        nested = "<aside" in inner
        if has_image or multi_para or nested:
            snippet = inner.strip().splitlines()[0][:50] if inner.strip() else ""
            flags.append(
                Flag(
                    section="blocking",
                    message="Auto-converted aside with images/multiple paragraphs; "
                    "verify admonition body renders correctly.",
                    locator=snippet,
                )
            )
        return f"!!! {kind}\n{indented}"

    return _ASIDE_RE.sub(repl, body), flags
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_asides.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/asides.py migration/tests/test_asides.py
git commit -m "feat(migration): convert CLaaT asides to Material admonitions"
```

---

### Task 5: Link converter + broken-link detection

**Files:**
- Create: `migration/claat/links.py`
- Test: `migration/tests/test_links.py`

**Interfaces:**
- Consumes: `Flag` from `migration.claat.models`.
- Produces: `convert_links(body: str) -> tuple[str, list[Flag]]` — rewrites `<a href="URL" target="_blank">TEXT</a>` → `[TEXT](URL){target="_blank"}` and plain `<a href="URL">TEXT</a>` → `[TEXT](URL)`; flags Markdown links with empty targets (`]( )`) as `blocking`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_links.py`

```python
from migration.claat.links import convert_links


def test_target_blank_link_converted():
    out, flags = convert_links('See <a href="https://x.io/" target="_blank">X</a>.')
    assert "[X](https://x.io/){target=\"_blank\"}" in out


def test_plain_anchor_converted():
    out, flags = convert_links('<a href="https://y.io">Y</a>')
    assert "[Y](https://y.io)" in out


def test_empty_markdown_target_flagged():
    out, flags = convert_links("See [broken]( ) here.")
    assert any(f.section == "blocking" for f in flags)


def test_multiline_anchor_text_converted():
    out, flags = convert_links('<a href="https://z.io/" target="_blank">Two\nlines</a>')
    assert "[Two\nlines](https://z.io/){target=\"_blank\"}" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_links.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.links'`

- [ ] **Step 3: Write `migration/claat/links.py`**

```python
import re

from migration.claat.models import Flag

_TARGET_RE = re.compile(
    r'<a\s+href="([^"]*)"[^>]*target="_blank"[^>]*>(.*?)</a>', re.DOTALL
)
_PLAIN_RE = re.compile(r'<a\s+href="([^"]*)"\s*>(.*?)</a>', re.DOTALL)
_EMPTY_TARGET_RE = re.compile(r"\]\(\s*\)")


def convert_links(body: str) -> tuple[str, list[Flag]]:
    body = _TARGET_RE.sub(r'[\2](\1){target="_blank"}', body)
    body = _PLAIN_RE.sub(r"[\2](\1)", body)
    flags: list[Flag] = []
    for m in _EMPTY_TARGET_RE.finditer(body):
        flags.append(
            Flag(
                section="blocking",
                message="Markdown link with empty target — fix or remove.",
                locator=body[max(0, m.start() - 20): m.start()].splitlines()[-1]
                if body[:m.start()].strip() else "",
            )
        )
    return body, flags
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_links.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/links.py migration/tests/test_links.py
git commit -m "feat(migration): convert HTML anchors to markdown, flag empty links"
```

---

### Task 6: List re-indenter (fence-aware)

**Files:**
- Create: `migration/claat/lists.py`
- Test: `migration/tests/test_lists.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `reindent_lists(body: str) -> str` — outside fenced code blocks, snaps any line indented ≥3 spaces to `floor(indent/4)*4` with a minimum of 4; leaves 0–2 space indents and fenced-code lines untouched.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_lists.py`

```python
from migration.claat.lists import reindent_lists


def test_five_space_indent_snaps_to_four():
    assert reindent_lists("1. item\n     ![image](img/x.png)\n") == (
        "1. item\n    ![image](img/x.png)\n"
    )


def test_eight_space_indent_preserved():
    assert reindent_lists("1. item\n        deep\n") == "1. item\n        deep\n"


def test_code_fence_content_untouched():
    src = "```\n     preserve me\n```\n"
    assert reindent_lists(src) == src


def test_shallow_indent_untouched():
    assert reindent_lists("  two spaces\n") == "  two spaces\n"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_lists.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.lists'`

- [ ] **Step 3: Write `migration/claat/lists.py`**

```python
import re

_FENCE_RE = re.compile(r"^\s*```")


def reindent_lists(body: str) -> str:
    out = []
    in_fence = False
    for line in body.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent >= 3 and stripped:
            new_indent = max(4, (indent // 4) * 4)
            out.append(" " * new_indent + stripped)
        else:
            out.append(line)
    trailing = "\n" if body.endswith("\n") else ""
    return "\n".join(out) + trailing
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_lists.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/lists.py migration/tests/test_lists.py
git commit -m "feat(migration): fence-aware list continuation re-indenter"
```

---

### Task 7: Image processor

**Files:**
- Create: `migration/claat/images.py`
- Test: `migration/tests/test_images.py`

**Interfaces:**
- Consumes: `Flag` from `migration.claat.models`; `slug_filename` from `migration.claat.slugify`.
- Produces: `process_images(body: str, src_img_dir: pathlib.Path, dest_prefix: str) -> tuple[str, dict[str, str], list[Flag]]` — rewrites `![...](img/OLD)` to `![DERIVED_ALT](dest_prefix/NEWSLUG)`, returns `(new_body, rename_map, flags)` where `rename_map[OLD] = NEWSLUG` (basenames), one `alt`-section flag per image, and a `blocking` flag for any referenced file absent from `src_img_dir`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_images.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_images.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.images'`

- [ ] **Step 3: Write `migration/claat/images.py`**

```python
import pathlib
import re

from migration.claat.models import Flag
from migration.claat.slugify import slug_filename

_IMG_RE = re.compile(r"!\[[^\]]*\]\(img/([^)]+)\)")


def _alt_from_slug(slug: str) -> str:
    stem = slug.rsplit(".", 1)[0]
    return stem.replace("-", " ").replace("_", " ").strip()


def process_images(
    body: str, src_img_dir: pathlib.Path, dest_prefix: str
) -> tuple[str, dict[str, str], list[Flag]]:
    renames: dict[str, str] = {}
    flags: list[Flag] = []

    def repl(m: "re.Match") -> str:
        orig = m.group(1)
        new = slug_filename(orig)
        renames[orig] = new
        alt = _alt_from_slug(new)
        if not (src_img_dir / orig).exists():
            flags.append(
                Flag(
                    section="blocking",
                    message=f"Referenced image not found on disk: img/{orig}",
                    locator=f"{dest_prefix}/{new}",
                )
            )
        flags.append(
            Flag(
                section="alt",
                message=f"Alt text auto-derived ('{alt}') — confirm it reads sensibly.",
                locator=f"{dest_prefix}/{new}",
            )
        )
        return f"![{alt}]({dest_prefix}/{new})"

    return _IMG_RE.sub(repl, body), renames, flags
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_images.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/claat/images.py migration/tests/test_images.py
git commit -m "feat(migration): image ref rewriter, filename slugging, alt flags"
```

---

### Task 8: Document orchestrator

**Files:**
- Create: `migration/claat/document.py`
- Test: `migration/tests/test_document.py`

**Interfaces:**
- Consumes: `parse_header`, `convert_asides`, `strip_duration`, `convert_links`, `reindent_lists`, `process_images`, `Flag`.
- Produces: `ConvertedDoc` dataclass with fields `markdown: str`, `metadata: dict`, `title: str`, `total_minutes: int`, `image_renames: dict[str, str]`, `flags: list[Flag]`; and `convert_document(readme_text: str, src_img_dir: pathlib.Path, labslug: str) -> ConvertedDoc`. Applies transforms in order **asides → duration → links → lists → images**, extracts the first `# ` heading as `title`, flags stale `feedback_link` domains as `blocking`, and resolves each flag's `line` from its `locator` against the final markdown.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_document.py`

```python
import pathlib

from migration.claat.document import convert_document

FIXROOT = pathlib.Path(__file__).parent / "fixtures" / "sample_claat"


def test_convert_document_end_to_end():
    text = (FIXROOT / "README.md").read_text()
    doc = convert_document(text, FIXROOT / "img", "lab0")
    # header lifted
    assert doc.metadata["id"] == "sample-lab"
    assert doc.title == "Sample Fixture Lab - One Of Each"
    # durations summed and removed from visible body
    assert doc.total_minutes == 8
    assert "Duration: 3\n" not in doc.markdown
    # aside converted
    assert "!!! tip" in doc.markdown
    assert "!!! warning" in doc.markdown
    # link converted
    assert '{target="_blank"}' in doc.markdown
    # image rewritten with prefix + slug
    assert "](img/lab0/pic-one.png)" in doc.markdown
    assert doc.image_renames["pic one.png"] == "pic-one.png"


def test_stale_feedback_link_flagged():
    text = (FIXROOT / "README.md").read_text()
    doc = convert_document(text, FIXROOT / "img", "lab0")
    assert any(
        f.section == "blocking" and "feedback" in f.message.lower() for f in doc.flags
    )


def test_flags_have_resolved_line_numbers():
    text = (FIXROOT / "README.md").read_text()
    doc = convert_document(text, FIXROOT / "img", "lab0")
    # at least one flag resolved to a real (non-zero) line
    assert any(f.line > 0 for f in doc.flags)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_document.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.claat.document'`

- [ ] **Step 3: Write `migration/claat/document.py`**

```python
import pathlib
import re
from dataclasses import dataclass, field

from migration.claat.asides import convert_asides
from migration.claat.duration import strip_duration
from migration.claat.header import parse_header
from migration.claat.images import process_images
from migration.claat.links import convert_links
from migration.claat.lists import reindent_lists
from migration.claat.models import Flag

_STALE_FEEDBACK = ("workshops-content", "claat-mockup", "mailto:")
_H1_RE = re.compile(r"^#\s+(.*)$", re.MULTILINE)


@dataclass
class ConvertedDoc:
    markdown: str
    metadata: dict
    title: str
    total_minutes: int
    image_renames: dict
    flags: list = field(default_factory=list)


def _resolve_lines(markdown: str, flags: list[Flag]) -> None:
    lines = markdown.splitlines()
    for f in flags:
        if not f.locator:
            continue
        for idx, ln in enumerate(lines, start=1):
            if f.locator in ln:
                f.line = idx
                break


def convert_document(
    readme_text: str, src_img_dir: pathlib.Path, labslug: str
) -> ConvertedDoc:
    meta, body = parse_header(readme_text)
    title_m = _H1_RE.search(body)
    title = title_m.group(1).strip() if title_m else labslug

    body, aside_flags = convert_asides(body)
    body, total = strip_duration(body)
    body, link_flags = convert_links(body)
    body = reindent_lists(body)
    body, renames, img_flags = process_images(body, src_img_dir, f"img/{labslug}")

    flags = aside_flags + link_flags + img_flags
    fb = meta.get("feedback_link", "")
    if any(s in fb for s in _STALE_FEEDBACK):
        flags.append(
            Flag(
                section="blocking",
                message=f"Stale Feedback Link ({fb}) — replace with the repo feedback link.",
            )
        )

    markdown = body.strip() + "\n"
    _resolve_lines(markdown, flags)
    return ConvertedDoc(
        markdown=markdown,
        metadata=meta,
        title=title,
        total_minutes=total,
        image_renames=renames,
        flags=flags,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_document.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run the whole suite**

Run: `python3 -m pytest migration/tests/ -v`
Expected: PASS (all tasks 1–8 green)

- [ ] **Step 6: Commit**

```bash
git add migration/claat/document.py migration/tests/test_document.py
git commit -m "feat(migration): document orchestrator combining all transforms"
```

---

### Task 9: `convert.py` CLI (family → docs + images + nav + log)

**Files:**
- Create: `migration/convert.py`
- Test: `migration/tests/test_convert_cli.py`

**Interfaces:**
- Consumes: `convert_document`, `ConvertedDoc`, `natural_key`, `slug_text`.
- Produces: `convert_family(src_family_dir, out_repo_dir, strip_prefix="") -> dict` (the transform-log dict) and a `main(argv)` CLI. Writes `out_repo_dir/docs/<n>-<labslug>.md`, copies renamed images into `out_repo_dir/docs/img/<labslug>/`, replaces the `# NAV_PLACEHOLDER` line in `out_repo_dir/mkdocs.yaml` with the built nav (Welcome first), and writes `out_repo_dir/transform_log.json`. Lab dirs are ordered by `natural_key`; `labslug = slug_text(dir_name minus strip_prefix)`. Adds one `screenshot`-section and one `judgment`-section flag per lab.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_convert_cli.py`

```python
import json
import pathlib

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_convert_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.convert'`

- [ ] **Step 3: Write `migration/convert.py`**

```python
import argparse
import json
import pathlib
import shutil
import sys
from dataclasses import asdict

from migration.claat.document import convert_document
from migration.claat.slugify import natural_key, slug_text


def _lab_dirs(src_family_dir: pathlib.Path) -> list[pathlib.Path]:
    dirs = [p for p in src_family_dir.iterdir() if p.is_dir()]
    return sorted(dirs, key=lambda p: natural_key(p.name))


def convert_family(
    src_family_dir: pathlib.Path,
    out_repo_dir: pathlib.Path,
    strip_prefix: str = "",
) -> dict:
    src_family_dir = pathlib.Path(src_family_dir)
    out_repo_dir = pathlib.Path(out_repo_dir)
    docs = out_repo_dir / "docs"
    labs_log = []
    nav_lines = ['  - "Welcome": index.md']

    for i, d in enumerate(_lab_dirs(src_family_dir), start=1):
        name = d.name
        labslug = slug_text(name[len(strip_prefix):] if name.startswith(strip_prefix) else name)
        doc = convert_document((d / "README.md").read_text(), d / "img", labslug)
        page = f"{i}-{labslug}.md"
        (docs / page).write_text(doc.markdown)

        img_out = docs / "img" / labslug
        img_out.mkdir(parents=True, exist_ok=True)
        for orig, new in doc.image_renames.items():
            src_img = d / "img" / orig
            if src_img.exists():
                shutil.copyfile(src_img, img_out / new)

        flags = [asdict_flag(f) for f in doc.flags]
        flags.append({"section": "screenshot", "message":
                      f"Run this lab and verify its {len(doc.image_renames)} "
                      f"screenshots are current (technical-accuracy gate).",
                      "locator": "", "line": 0})
        flags.append({"section": "judgment", "message":
                      "Confirm this lab still belongs in the migrated workshop.",
                      "locator": "", "line": 0})

        nav_lines.append(f'  - "{i}. {doc.title}": {page}')
        labs_log.append({
            "labslug": labslug, "source": name, "page": f"docs/{page}",
            "title": doc.title, "total_minutes": doc.total_minutes,
            "image_count": len(doc.image_renames), "flags": flags,
            "metadata": doc.metadata,
        })

    # inject nav
    mk = out_repo_dir / "mkdocs.yaml"
    mk.write_text(mk.read_text().replace("# NAV_PLACEHOLDER", "\n".join(nav_lines)))

    log = {"repo": out_repo_dir.name, "labs": labs_log}
    (out_repo_dir / "transform_log.json").write_text(json.dumps(log, indent=2))
    return log


def asdict_flag(f) -> dict:
    return {"section": f.section, "message": f.message, "locator": f.locator, "line": f.line}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Convert a CLaaT workshop family.")
    ap.add_argument("src_family_dir")
    ap.add_argument("out_repo_dir")
    ap.add_argument("--strip-prefix", default="")
    args = ap.parse_args(argv)
    log = convert_family(args.src_family_dir, args.out_repo_dir, args.strip_prefix)
    print(f"Converted {len(log['labs'])} labs into {args.out_repo_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_convert_cli.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/convert.py migration/tests/test_convert_cli.py
git commit -m "feat(migration): convert.py CLI — family to docs, images, nav, log"
```

---

### Task 10: `scaffold.py` CLI (repo skeleton from template)

**Files:**
- Create: `migration/scaffold.py`
- Test: `migration/tests/test_scaffold.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `scaffold_repo(out_repo_dir, *, site_name, repo_url, template_dir, framework_dir) -> None` and a `main(argv)` CLI. Copies the template tree, overlays the framework's `mkdocs-base.yaml` (repo root) and `docs/stylesheets/extra.css`, removes template top-level `docs/*.md` pages, writes a minimal `docs/index.md`, and writes `mkdocs.yaml` containing `INHERIT: mkdocs-base.yaml`, `site_name`, `repo_url`, a `nav:` block ending in `# NAV_PLACEHOLDER`, and an empty `extra.rum_snippet`.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_scaffold.py`

```python
import pathlib

from migration.scaffold import scaffold_repo

TEMPLATE = pathlib.Path("/home/ubuntu/workspace/dynatrace-codespaces/enablement-codespaces-template")
FRAMEWORK = pathlib.Path("/home/ubuntu/workspace/dynatrace-codespaces/codespaces-framework")


def test_scaffold_produces_buildable_skeleton(tmp_path):
    out = tmp_path / "enablement-demo"
    scaffold_repo(
        out, site_name="Demo Lab", repo_url="https://github.com/x/enablement-demo",
        template_dir=TEMPLATE, framework_dir=FRAMEWORK,
    )
    assert (out / "mkdocs-base.yaml").exists()
    assert (out / "docs" / "stylesheets" / "extra.css").exists()
    assert (out / "docs" / "overrides" / "main.html").exists()
    assert (out / "docs" / "index.md").exists()
    mk = (out / "mkdocs.yaml").read_text()
    assert "INHERIT: mkdocs-base.yaml" in mk
    assert 'site_name: "Demo Lab"' in mk
    assert "# NAV_PLACEHOLDER" in mk


def test_scaffold_clears_template_pages(tmp_path):
    out = tmp_path / "enablement-demo"
    scaffold_repo(
        out, site_name="Demo Lab", repo_url="https://github.com/x/enablement-demo",
        template_dir=TEMPLATE, framework_dir=FRAMEWORK,
    )
    # template's own numbered content pages should be gone
    assert not (out / "docs" / "2-getting-started.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_scaffold.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.scaffold'`

- [ ] **Step 3: Write `migration/scaffold.py`**

```python
import argparse
import pathlib
import shutil
import sys

_KEEP_DOCS_DIRS = {"overrides", "snippets", "requirements", "stylesheets", "img"}

_MKDOCS_TEMPLATE = """INHERIT: mkdocs-base.yaml

site_name: "{site_name}"
repo_name: "View Code on GitHub"
repo_url: "{repo_url}"
nav:
# NAV_PLACEHOLDER

extra:
  rum_snippet: ""  # TODO: paste this repo's Dynatrace RUM snippet before go-live
"""

_INDEX = """# {site_name}

Workshop overview. Migrated from Google CLaaT.

<!-- TODO: write a short workshop intro here. -->
"""


def scaffold_repo(
    out_repo_dir,
    *,
    site_name: str,
    repo_url: str,
    template_dir,
    framework_dir,
) -> None:
    out = pathlib.Path(out_repo_dir)
    template_dir = pathlib.Path(template_dir)
    framework_dir = pathlib.Path(framework_dir)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(
        template_dir, out,
        ignore=shutil.ignore_patterns(".git", ".cache", "mkdocs-base.yaml"),
    )
    # overlay framework-owned build assets (fetched by CI in real life)
    shutil.copyfile(framework_dir / "mkdocs-base.yaml", out / "mkdocs-base.yaml")
    (out / "docs" / "stylesheets").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        framework_dir / "docs" / "stylesheets" / "extra.css",
        out / "docs" / "stylesheets" / "extra.css",
    )
    # clear template top-level content pages; keep infra dirs
    docs = out / "docs"
    for p in docs.glob("*.md"):
        p.unlink()
    (docs / "index.md").write_text(_INDEX.format(site_name=site_name))
    (out / "mkdocs.yaml").write_text(
        _MKDOCS_TEMPLATE.format(site_name=site_name, repo_url=repo_url)
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a framework repo from the template.")
    ap.add_argument("out_repo_dir")
    ap.add_argument("--site-name", required=True)
    ap.add_argument("--repo-url", required=True)
    ap.add_argument("--template-dir", default="../enablement-codespaces-template")
    ap.add_argument("--framework-dir", default="../codespaces-framework")
    args = ap.parse_args(argv)
    scaffold_repo(
        args.out_repo_dir, site_name=args.site_name, repo_url=args.repo_url,
        template_dir=args.template_dir, framework_dir=args.framework_dir,
    )
    print(f"Scaffolded {args.out_repo_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_scaffold.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add migration/scaffold.py migration/tests/test_scaffold.py
git commit -m "feat(migration): scaffold.py CLI — framework repo skeleton from template"
```

---

### Task 11: `review.py` (REVIEW.md + repos.yaml snippet + tracker)

**Files:**
- Create: `migration/review.py`
- Test: `migration/tests/test_review.py`

**Interfaces:**
- Consumes: the `transform_log.json` dict schema produced by `convert_family` (Task 9).
- Produces: `build_review(log: dict, repo_dir) -> str` writing `<repo_dir>/REVIEW.md`, and `repos_yaml_snippet(log: dict, repo_name, title, tags, duration) -> str`; plus a `main(argv)` CLI. `REVIEW.md` has sections 0–5 (context, blocking, screenshot/run, alt, judgment, definition-of-done) with per-section checkbox items carrying `page:line` pointers and per-section counts.

- [ ] **Step 1: Write the failing test** — `migration/tests/test_review.py`

```python
from migration.review import build_review, repos_yaml_snippet

LOG = {
    "repo": "enablement-demo",
    "labs": [
        {"labslug": "lab0", "source": "demo-lab0", "page": "docs/1-lab0.md",
         "title": "Demo Lab 0", "total_minutes": 8, "image_count": 2,
         "metadata": {"authors": "Test Author"},
         "flags": [
             {"section": "blocking", "message": "Stale Feedback Link", "locator": "", "line": 0},
             {"section": "alt", "message": "Alt derived", "locator": "", "line": 5},
             {"section": "screenshot", "message": "Run this lab", "locator": "", "line": 0},
             {"section": "judgment", "message": "Confirm belongs", "locator": "", "line": 0},
         ]},
    ],
}


def test_build_review_has_all_sections(tmp_path):
    md = build_review(LOG, tmp_path)
    assert "## 1. Blocking" in md
    assert "## 2. Run & re-capture" in md
    assert "## 3. Alt-text review" in md
    assert "## 4. Judgment calls" in md
    assert "## 5. Definition of done" in md
    assert (tmp_path / "REVIEW.md").exists()


def test_blocking_item_has_page_pointer(tmp_path):
    md = build_review(LOG, tmp_path)
    assert "docs/1-lab0.md" in md
    assert "- [ ]" in md


def test_repos_yaml_snippet_fields():
    snip = repos_yaml_snippet(LOG, "enablement-demo", "Demo", ["demo"], "1h")
    assert "name: enablement-demo" in snip
    assert "title: \"Demo\"" in snip
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest migration/tests/test_review.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'migration.review'`

- [ ] **Step 3: Write `migration/review.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest migration/tests/test_review.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run the full suite**

Run: `python3 -m pytest migration/tests/ -v`
Expected: PASS (all green)

- [ ] **Step 6: Commit**

```bash
git add migration/review.py migration/tests/test_review.py
git commit -m "feat(migration): review.py — REVIEW.md, repos.yaml snippet"
```

---

### Task 12: Azure Grail pilot — run end-to-end and verify strict build

**Files:**
- Create: `migration/README.md`
- Create (generated, git-ignored): `migration/out/enablement-azure-grail/`

**Interfaces:**
- Consumes: `scaffold.py`, `convert.py`, `review.py` CLIs.
- Produces: a locally-built `enablement-azure-grail` repo under `migration/out/` plus `migration/README.md` documenting the pipeline.

- [ ] **Step 1: Install MkDocs Material (framework-pinned)**

Run:
```bash
cd /home/ubuntu/workspace/dynatrace-codespaces/learn-site-content
python3 -m pip install --quiet -r enablement-codespaces-template/docs/requirements/requirements-mkdocs.txt
python3 -m pip show mkdocs-material | grep -i version
```
Expected: `Version: 9.5.42`

- [ ] **Step 2: Scaffold the pilot repo**

Run:
```bash
python3 -m migration.scaffold migration/out/enablement-azure-grail \
  --site-name "Dynatrace Enablement Lab: Azure Grail" \
  --repo-url "https://github.com/dynatrace-wwse/enablement-azure-grail"
```
Expected: `Scaffolded migration/out/enablement-azure-grail`

- [ ] **Step 3: Convert the Grail family into the scaffolded repo**

Run:
```bash
python3 -m migration.convert \
  "workshop-markdown" \
  migration/out/enablement-azure-grail \
  --strip-prefix "azure-grail-" 2>&1 | tail -2
```
Wait — `convert_family` expects a family dir whose immediate children are the labs. Grail labs sit directly under `workshop-markdown/`. Create a filtered family view first:

```bash
mkdir -p migration/out/_grail-src
for d in workshop-markdown/azure-grail-lab*; do ln -s "$(pwd)/$d" "migration/out/_grail-src/$(basename "$d")"; done
python3 -m migration.convert \
  migration/out/_grail-src \
  migration/out/enablement-azure-grail \
  --strip-prefix "azure-grail-"
```
Expected: `Converted 6 labs into migration/out/enablement-azure-grail`

- [ ] **Step 4: Generate the REVIEW.md and repos.yaml snippet**

Run:
```bash
python3 -m migration.review migration/out/enablement-azure-grail \
  --title "Azure Grail" --tags "azure,grail,kubernetes" --duration "2h"
```
Expected: `Wrote migration/out/enablement-azure-grail/REVIEW.md and repos.yaml snippet`

- [ ] **Step 5: Build the site with strict mode**

Run:
```bash
cd migration/out/enablement-azure-grail && python3 -m mkdocs build --strict 2>&1 | tail -20; cd /home/ubuntu/workspace/dynatrace-codespaces/learn-site-content
```
Expected: build finishes with `INFO - Documentation built in ...` and **no `WARNING`/`ERROR`** lines (strict mode fails on any warning). If it fails on a missing-image or bad-link warning, that is a real converter finding — capture it, add/adjust a unit test for the rule, fix the transform, and re-run from Step 3.

- [ ] **Step 6: Sanity-check the output by eye**

Run:
```bash
ls migration/out/enablement-azure-grail/docs/*.md
echo "--- blocking count ---"; grep -c '^- \[ \]' migration/out/enablement-azure-grail/REVIEW.md
sed -n '1,40p' migration/out/enablement-azure-grail/REVIEW.md
```
Expected: 7 pages (`index.md` + `1-lab0.md`…`6-lab5.md`); `REVIEW.md` lists blocking/screenshot/alt/judgment items with `docs/…:line` pointers.

- [ ] **Step 7: Write `migration/README.md`** (pipeline runbook)

```markdown
# CLaaT → Codespaces Migration Toolkit

One-time tooling to convert Google CLaaT workshops into Codespaces-framework repos.
See the design spec: `docs/superpowers/specs/2026-07-20-claat-to-codespaces-migration-design.md`.

**Branch-only:** generated repos land in `migration/out/` (git-ignored). Do NOT PR to
main, register in the framework `repos.yaml`, or publish until the owner lifts the hold.

## Install
    python3 -m pip install -r enablement-codespaces-template/docs/requirements/requirements-mkdocs.txt
    python3 -m pip install -r migration/requirements.txt

## Run a family (example: Azure Grail)
    # 1. filtered source view (labs must be direct children of the family dir)
    mkdir -p migration/out/_grail-src
    for d in workshop-markdown/azure-grail-lab*; do ln -s "$(pwd)/$d" "migration/out/_grail-src/$(basename "$d")"; done

    # 2. scaffold -> convert -> review
    python3 -m migration.scaffold migration/out/enablement-azure-grail \
      --site-name "Dynatrace Enablement Lab: Azure Grail" \
      --repo-url "https://github.com/dynatrace-wwse/enablement-azure-grail"
    python3 -m migration.convert migration/out/_grail-src migration/out/enablement-azure-grail \
      --strip-prefix "azure-grail-"
    python3 -m migration.review migration/out/enablement-azure-grail \
      --title "Azure Grail" --tags "azure,grail,kubernetes" --duration "2h"

    # 3. verify
    (cd migration/out/enablement-azure-grail && python3 -m mkdocs build --strict)

## Then
Open `migration/out/enablement-azure-grail/REVIEW.md` — that is the bounded human
task packet. Work its checkboxes; done = all boxes checked + strict build clean.

## Test
    python3 -m pytest migration/tests/ -v
```

- [ ] **Step 8: Run the full test suite one final time**

Run: `python3 -m pytest migration/tests/ -v`
Expected: PASS (all green)

- [ ] **Step 9: Commit the toolkit (branch-only; generated output stays ignored)**

```bash
git add migration/README.md
git status --short migration/out || true   # confirm migration/out/ is NOT staged (git-ignored)
git commit -m "docs(migration): pipeline runbook; Grail pilot builds strict-clean"
```

---

## Self-Review notes (author check against spec)

- **Spec §5 transform rules 1–15:** headers (T2), summary/tags→metadata (T2+T11), H1 title (T8), Duration (T3), positive/negative asides (T4), image slug+alt (T7), space/zero-width dir & file names (T1 slug, T7), `<a target>` (T5), raw tables/`<br>`/emoji (left untouched by design — no transform touches them, verified by asides/links regexes being specific), repeated-`1.` list re-indent (T6), cloud prose untouched (no rule targets it), broken/stale links (T5 empty-target, T8 stale feedback). **Covered.**
- **Spec §6 REVIEW.md sections 0–5 + severity tiers + counts + repos.yaml snippet:** T11. **Covered.**
- **Spec §7 pilot = Azure Grail + strict-build gate + converter fixture test:** T12 + fixture in T1. **Covered.**
- **Branch-only / no-publish constraint:** every commit targets `feat/claat-migration-toolkit`; `migration/out/` git-ignored (T1); REVIEW.md §5 and README restate the hold. **Covered.**
- **Out of scope (OpenShift/JP/Unused/live-env):** the CLI operates only on the family dir it is pointed at; nothing auto-discovers excluded content. **Covered.**
- **Placeholder scan:** the only literal `TODO:` strings are intentional authoring markers emitted into generated artifacts (index.md, mkdocs rum_snippet, repos.yaml snippet), not gaps in the plan. **OK.**
- **Type consistency:** `Flag(section,message,locator,line)` used identically across T4/T5/T7/T8; `ConvertedDoc` fields consumed by `convert_family` match T8 definitions; `transform_log.json` schema written in T9 matches what T11 reads. **OK.**
