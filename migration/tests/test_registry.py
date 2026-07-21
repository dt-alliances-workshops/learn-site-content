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
