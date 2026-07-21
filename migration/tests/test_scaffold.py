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
