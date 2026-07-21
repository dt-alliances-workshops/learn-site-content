import argparse
import pathlib
import shutil
import sys

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
