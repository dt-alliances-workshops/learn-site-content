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
