from migration.review import build_review, repos_yaml_snippet

LOG = {
    "repo": "enablement-demo",
    "labs": [
        {"labslug": "lab0", "source": "demo-lab0", "page": "docs/1-lab0.md",
         "id": "sample-lab-id",
         "title": "Demo Lab 0", "total_minutes": 8, "image_count": 2,
         "metadata": {"authors": "Test Author"},
         "flags": [
             {"section": "blocking", "message": "Stale Feedback Link", "locator": "", "line": 0},
             {"section": "alt", "message": "Alt derived", "locator": "", "line": 5},
             {"section": "screenshot", "message": "Run this lab", "locator": "", "line": 0},
             {"section": "judgment", "message": "Confirm belongs", "locator": "", "line": 0},
             {"section": "env", "message": "References a cloud account", "locator": "", "line": 0},
         ]},
    ],
}


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


def test_blocking_item_has_page_pointer(tmp_path):
    md = build_review(LOG, tmp_path)
    assert "docs/1-lab0.md" in md
    assert "- [ ]" in md


def test_repos_yaml_snippet_fields():
    snip = repos_yaml_snippet(LOG, "enablement-demo", "Demo", ["demo"], "1h")
    assert "name: enablement-demo" in snip
    assert "title: \"Demo\"" in snip
