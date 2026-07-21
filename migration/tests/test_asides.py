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
