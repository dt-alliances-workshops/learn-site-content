# CLaaT Migration — Toolkit Hardening & Fan-Out Design

**Date:** 2026-07-21
**Author:** akirasoft (with Claude)
**Status:** Approved design, pending implementation plan
**Predecessor:** [2026-07-20 toolkit + Grail pilot design](2026-07-20-claat-to-codespaces-migration-design.md)

---

## 1. Goal

Harden the one-time CLaaT→Codespaces migration toolkit to clear the deferred
items from the pilot's final review, run the pipeline across the remaining
workshops, and package all output on one branch for teammate validation.

**Constraint (unchanged, hard):** branch-only. No PR to `main`, no framework
`repos.yaml` registration, no GitHub Pages publish. All output ships on a single
review branch. See [[claat-migration-branch-only]].

---

## 2. Domain correction — variants are separate workshops

The AWS "variants" (Immersion Day / SAAS / Serverless / Self-paced) are **not**
sections of one workshop. Each is a distinct workshop, and the same lab is
deliberately **shared across several of them** — exactly the original CLaaT
"views" model (`app/views/*.json` selected labs into a landing page by tag).

Consequence: the framework mapping is **one repo per workshop/view**, and a
shared lab is emitted into every repo it belongs to (content duplication is
expected and correct — each repo is a standalone workshop/Codespace). This
supersedes the predecessor spec's "consolidate AWS into one repo" decision.

---

## 3. Toolkit hardening

### 3.1 View/workshop registry (the significant new piece)
Replace the ad-hoc `--strip-prefix` CLI with a declarative registry — one entry
per target repo — each with a **lab selector**:

- `dir_glob` (e.g. `azure-grail-lab*`): selects labs whose directory name matches
  the glob. Keeps the linear Azure workshops (and the proven Grail pilot) working.
- `tag` (e.g. `aws-immersion-day-saas`): selects labs whose CLaaT `tags` header
  contains the tag (whitespace-normalized). Resurrects the views model; a lab
  tagged for N workshops is emitted into N repos.

A **view-based runner** scans the whole `workshop-markdown/` corpus once, reads
each lab's header, and selects matches per registry entry. This **eliminates the
pilot's symlink workaround** (`migration/out/_grail-src`). Lab order within a
workshop is `natural_key` on the directory name (handles numeric gaps, e.g.
Serverless = labs 0/11/12).

**Orphan guard:** any active lab (excluding JP variants, `Unused/`, and
RedHat/OpenShift) that matches no registry selector is reported as unassigned in
the tracker. Nothing is silently dropped.

### 3.2 CLaaT `id` capture
Keep clean directory-name page slugs (old CLaaT site is discarded; URL continuity
is not a requirement; structure is provisional). Surface each lab's original
`id:` in the `transform_log.json` and in REVIEW.md §0's lab→page map for
traceability.

### 3.3 Cloud-prose heuristic flag (spec rule 14)
A keyword scan of each lab body for cloud-account/portal terms — `Azure Portal`,
`AWS Console`, `Azure Pass`, `promo code`, `subscription`, `credentials`
(case-insensitive) — emits ONE non-blocking `env`-section REVIEW item per lab
that hits: "references a cloud account/portal; confirm docs-first wording." It
points validators at the BYO-cloud dependencies the docs-first model leaves in
prose. Not auto-repaired (not reliably derivable).

### 3.4 MIGRATION-TRACKER.md generator (spec §6)
After the fan-out, generate `migration/out/MIGRATION-TRACKER.md`: one row per
produced repo with workshop title, lab count, per-section flag counts (blocking /
env / screenshot / alt / judgment), an **Assignee** column (`TODO` for the owner
to fill), and a Status column. Plus an "Unassigned labs" section listing any
orphans from 3.1. This is the map for a non-git-native team working one branch.

### 3.5 Cosmetic cleanups
Delete dead `asdict` import (`convert.py`) and dead `_KEEP_DOCS_DIRS`
(`scaffold.py`).

All changes are TDD'd against fixtures. Existing 40 tests must stay green.

---

## 4. Fan-out targets

Grail is already done (pilot). Registry entries to add and run:

| Repo | Selector | ~Labs |
|---|---|---|
| `enablement-azure-aks-levelup` | dir_glob `azure-aks-levelup-lab*` | 4 |
| `enablement-azure-gen2` | dir_glob `azure-lab*` | 11 |
| `enablement-aws-immersion-day` | tag `aws-immersion-day` | ~13 |
| `enablement-aws-immersion-day-saas` | tag `aws-immersion-day-saas` | ~13 |
| `enablement-aws-serverless` | tag `aws-immersion-day-serverless` | ~5 |
| `enablement-aws-selfpaced` | tag `aws-selfpaced` | ~14 |

`dir_glob azure-lab*` must not capture `azure-aks-levelup-lab*` or
`azure-grail-lab*` (it does not — those start `azure-aks`/`azure-grail`).

**Per-repo gate:** scaffold → convert → review → `mkdocs build --strict` clean.
A strict-build failure is a converter finding (fix + regression test), same
discipline as the pilot.

---

## 5. Handoff packaging

- **Single review branch `content-review`** carries the hardened toolkit plus all
  generated repos. Hardening + fan-out are performed on `feat/claat-migration-toolkit`;
  `content-review` is the clearly-named branch teammates check out.
- **`.gitignore`:** track generated repo *source* under `migration/out/`, but keep
  ignoring built `site/` output (`migration/out/**/site/`) and any scratch
  (`migration/out/_*`). Committed content is exactly what a teammate edits.
- **`migration/out/MIGRATION-TRACKER.md`** is the top-level map (§3.4).
- Each repo keeps its `REVIEW.md`. Branch pushed; **no PR, no main, no publish.**

Definition of done for a teammate remains: all their repo's REVIEW.md boxes
checked + `mkdocs build --strict` clean, on the branch (no merge).

---

## 6. Out of scope (unchanged)
JP variants; RedHat/OpenShift 101; `Unused/` archived labs; live cloud
provisioning; the Polymer/gulp/claat/S3 stack. Also out: per-lab content tabs /
cross-repo shared-lab includes (rejected in favor of one-repo-per-workshop with
duplication); framework `repos.yaml` registration and publishing (deferred until
the owner lifts the hold).

---

## 7. Open items for the fan-out run
- Final AWS lab→workshop membership depends on the real `tags` in each header;
  the orphan guard (§3.1) surfaces any lab that matches nothing so it can't be
  lost. Membership is validated during the run, not assumed here.
- `Dynatrace-SAAS-Prereq` (1 lab, its own CLaaT view): fold into the AWS SAAS
  workshop or emit as a tiny standalone repo — decided during the run based on
  whether other workshops depend on it.
