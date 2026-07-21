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
