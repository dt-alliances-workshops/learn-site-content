from migration.claat.links import convert_links


def test_target_blank_link_converted():
    out, flags = convert_links('See <a href="https://x.io/" target="_blank">X</a>.')
    assert "[X](https://x.io/){target=\"_blank\"}" in out


def test_plain_anchor_converted():
    out, flags = convert_links('<a href="https://y.io">Y</a>')
    assert "[Y](https://y.io)" in out


def test_empty_markdown_target_flagged():
    out, flags = convert_links("See [broken]( ) here.")
    assert any(f.section == "blocking" for f in flags)


def test_multiline_anchor_text_converted():
    out, flags = convert_links('<a href="https://z.io/" target="_blank">Two\nlines</a>')
    assert "[Two\nlines](https://z.io/){target=\"_blank\"}" in out
