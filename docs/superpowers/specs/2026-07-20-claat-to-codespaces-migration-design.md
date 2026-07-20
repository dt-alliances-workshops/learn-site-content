# CLaaT → Codespaces Framework Migration — Design

**Date:** 2026-07-20
**Author:** akirasoft (with Claude)
**Status:** Approved design, pending implementation plan

---

## 1. Goal

Convert the Google CLaaT (codelabs) workshops in `learn-site-content` into the
Dynatrace **Enablement Codespaces Framework** format (as used by
`enablement-kubernetes-101` et al.), producing **one repository per workshop
family**, each registered in the framework's `repos.yaml` and published to
GitHub Pages.

The overriding constraint: **keep human tasks tightly bound and well documented
before fanning them out to the team.** The automated converter must shrink and
standardize the human surface area so every teammate receives an identical,
finite, closeable work packet.

---

## 2. Source & target summary

### Source — `learn-site-content` (CLaaT)
- 57 codelabs (52 active + 5 archived under `Unused/`).
- Each codelab = one `README.md` + a flat `img/` folder.
- CLaaT-specific constructs actually in use are minimal:
  - Bare `key: value` metadata header (no YAML fences).
  - `## Heading` + a bare `Duration: N` line (128 occurrences, 20 files).
  - `<aside class="positive">` (159) / `<aside class="negative">` (6) info boxes.
  - Everything else is vanilla Markdown + light raw HTML (`<a target>`, `<br>`,
    `<table>` in RedHat files, `<b>/<i>`).
- 910 `![image](img/…)` references, all with alt text literally `"image"`.
- Build/publish stack (Polymer web components, gulp, `claat` Go binary, S3 +
  CloudFront) is **discarded, not migrated** — MkDocs Material replaces it.
- Navigation/audience grouping lives in `app/views/*.json` ("views"), not in the
  markdown — this encodes the family groupings.

### Target — Enablement Codespaces Framework
- Per-repo `mkdocs.yaml` with `INHERIT: mkdocs-base.yaml` (framework-owned theme,
  extensions, RUM). Repo supplies `site_name`, `repo_url`, `nav`, `rum_snippet`.
- Flat `docs/` — one markdown file per lab page, plus `img/`, `snippets/`,
  `overrides/`, `requirements/`.
- `.devcontainer/` pinned to a `FRAMEWORK_VERSION`, `post-create.sh` /
  `post-start.sh`, `util/` shell functions.
- `.github/workflows/` — GitHub Pages deploy + integration tests.
- Registration in `codespaces-framework/repos.yaml` (title, tags, duration,
  maintainer) to appear on `dynatrace-wwse.github.io`.
- No native per-lab folder / duration / checkpoint metadata — numbering lives in
  `nav:` labels and filenames; verification lives in `.devcontainer/test/`.

---

## 3. Scope decisions

| Decision | Choice |
|---|---|
| Repo granularity | **One repo per family** (~6 repos), not per codelab. |
| Live environment | **Docs-first** — standard devcontainer scaffold, minimal `post-create.sh`, no cloud provisioning. Labs reference the learner's own cloud account in prose, as today. Live automation added per-repo later. |
| Archived (`Unused/`) | **Excluded.** |
| Japanese variants (`*-jp`) | **Excluded** (i18n revisited later). |
| RedHat/OpenShift 101 (9 labs) | **Excluded** — the team no longer manages the RedHat relationship. |
| `status: Hidden` codelabs | **Included** (migrated). |
| AWS Immersion Day variants (SAAS/Serverless) | **Consolidated** into one AWS repo via tabs/sections, not separate repos. |

### Target repositories (~5, ~31 codelabs)
1. `enablement-azure-grail` — 6 labs *(pilot)*
2. `enablement-azure-aks-levelup` — 4 labs
3. `enablement-azure-gen2` — 11 labs
4. `enablement-aws-immersion-day` — ~22 labs (variant consolidation)
5. AWS Self-paced — folds into the AWS repo (final naming TBD during pilot)

---

## 4. Pipeline architecture

Nothing reaches a human until the machine has done everything deterministic.

```
learn-site-content/workshop-markdown/<family>/*/README.md + img/
        │
        ▼  [1] scaffold.py  — clone template → new repo skeleton
        ▼  [2] convert.py   — CLaaT md → framework docs/*.md, copy+rename images
        ▼  [3] mkdocs build --strict — must pass, zero warnings
        ▼  [4] emit REVIEW.md — the bounded human task packet (per repo)
        ▼  [ HUMAN ] follows REVIEW.md → commits → PR
        ▼  [5] repos.yaml entry + CI green → published to GitHub Pages
```

Both scripts live in a one-time `migration/` toolkit inside `learn-site-content`
(source repo). They are throwaway migration tooling, **not** framework code —
that is why extending the framework `sync` CLI (Approach C) was rejected. Steps
1–4 are fully automated and yield a repo that already builds; human work begins
only at a green MkDocs build.

---

## 5. Converter transform rules (`convert.py`)

Every rule is deterministic. Anything requiring judgment is **not** transformed —
it is flagged to `REVIEW.md`. The converter is idempotent and emits a per-file
JSON transform+flag log that feeds `REVIEW.md`.

| # | CLaaT source | Framework output | Auto / Flag |
|---|---|---|---|
| 1 | Bare `key: value` header block | Lifted to `mkdocs.yaml` + `repos.yaml`; deleted from body | Auto |
| 2 | `summary`/`authors`/`tags`/`categories`/`id`/`status` | `id`→page slug (URL continuity); `summary`→`repos.yaml description`; `tags`→`repos.yaml tags`; `authors`→`REVIEW.md` credits | Auto |
| 3 | `# H1` codelab title | Page H1 / nav label | Auto |
| 4 | `## Step` + `Duration: N` | `## Step` kept; `Duration:` removed from body, summed → total-time note, retained as HTML comment | Auto |
| 5 | `<aside class="positive">` (159) | `!!! tip "…"` with 4-space-indented body | Auto; multi-para/nested → Flag |
| 6 | `<aside class="negative">` (6) | `!!! warning` | Auto |
| 7 | `![image](img/x.png)` (910) | `![<derived alt>](img/x.png)`; images copied, spaces→hyphens | Auto; alt → Flag (batch) |
| 8 | Dir/id names with spaces (8) | Slugified (`aws-lab4 role`→`aws-lab4-role`) | Auto |
| 9 | `<a href … target="_blank">` (254) | `[text](url){target="_blank"}` | Auto |
| 10 | `<table>`/`<tr>` raw HTML | Left as raw HTML (`md_in_html`) | Auto; visual check → Flag *(the 3 known cases were RedHat, now out of scope)* |
| 11 | `<br>`/`<b>`/`<i>`/`<blockquote>` | Kept as-is | Auto |
| 12 | Repeated `1.` deep-indented lists | Re-indented to 4-space Python-Markdown | Auto |
| 13 | Emoji-as-semantics (`🔷`,`📓`,`💥💥💥`) | Preserved verbatim | Auto |
| 14 | Cloud-account / portal prose | Untouched | **Flag** (env decision is human) |
| 15 | Broken/empty links, stale Feedback URLs | Detected | **Flag** |

**Page model:** one CLaaT codelab = one framework `docs/` page (preserves lab
identity and URL slug). The family's labs become the numbered `nav:` sequence —
where lab0…lab12 ordering is set explicitly, fixing the lexical
lab10-before-lab2 problem. `Duration:` steps remain H2 sections *within* each lab
page, not separate files.

---

## 6. `REVIEW.md` — the bounded human packet

The converter emits one `REVIEW.md` at each generated repo's root. It is the
**only** document a teammate needs: **finite** (every item is a checkbox),
**located** (every item has a `file:line` pointer), **closeable** (done = all
boxes checked + CI green, no open-ended "good enough" judgment).

Sections:
0. **Context** (read once) — source paths, lab→page map, authors, env model.
1. **Blocking** — must resolve before PR (nested/low-confidence asides, stale/broken links).
2. **Run & re-capture** — refresh stale screenshots. **This is the technical-accuracy gate:** re-capturing a screenshot requires actually running the lab, so each item carries a "steps verified working" sub-check. No separate accuracy pass.
3. **Alt-text review** — batch-approvable; converter derived alt from filenames.
4. **Judgment calls** — does this lab still belong? (explicit owner decision)
5. **Definition of done** — all boxes checked, `mkdocs build --strict` clean, `repos.yaml` entry added (verbatim snippet provided), PR opened, integration CI green.

Properties that make fan-out tight:
- **Severity-tiered:** §1 blocks the PR; §2–3 are polish; §4 is explicit judgment.
- **Effort pre-estimated:** the converter counts items per section, so repos can
  be assigned by load, not guesswork.

A single top-level **`MIGRATION-TRACKER.md`** in the source repo tabulates all
repos × item counts × assignee × status for one-page fan-out and tracking.

---

## 7. Sequencing & validation

- **Pilot:** run the full pipeline on **Azure Grail** (6 labs, clean metadata,
  real `Duration:` data) as the reference conversion. Exercises every transform
  rule without AWS variant complexity. Validate + tune rules, then fan out.
- **Order after pilot (ascending difficulty):** Azure AKS LevelUp (4) →
  Azure Gen2 (11) → AWS Immersion Day (22, variant consolidation).
- **Validation gates per repo:** (1) `mkdocs build --strict` zero warnings at
  generation, (2) all `REVIEW.md` §1 boxes checked, (3) integration CI green.
- **Converter test:** a fixture CLaaT file containing one of each construct with
  asserted output, so rule regressions are caught.

### Explicitly out of scope
JP variants; RedHat/OpenShift 101 (relationship no longer team-managed);
`Unused/` archived labs; live cloud provisioning (docs-first); the
Polymer/gulp/`claat`/S3 stack (discarded, not migrated).

### Delivery constraints (hard)
- **Branch-only. No PR to `main` at this time.** Everything the migration
  produces is committed to branch(es) only. The `REVIEW.md` "Definition of done"
  and `MIGRATION-TRACKER.md` track branch readiness, **not** merge. The framework
  `repos.yaml` registration and GitHub Pages publication (pipeline step 5) are
  **deferred** — do not open PRs against `main` or publish until the owner
  explicitly lifts this hold.
- **Content structure is expected to change.** The source kept all content in one
  place; the framework is one repo per workshop. The final per-repo structure may
  diverge from a naive 1:1 port as we match the new framework — treat the
  per-repo `docs/` layout as provisional until the pilot validates it.

---

## 8. Open items to settle during the pilot
- Final naming + home for AWS Self-paced (own repo vs. section in AWS repo).
- Consolidation of the three divergent stale `Feedback Link:` targets into one
  repo-wide feedback link.
- Whether `Duration:` totals surface as a per-page badge or a single front-matter
  total-time field.
