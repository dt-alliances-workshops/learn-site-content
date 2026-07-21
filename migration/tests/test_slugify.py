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
