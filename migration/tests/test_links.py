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


def test_malformed_nested_bracket_link_flagged():
    # Real source authoring bug: destination starts with a stray '[' so the
    # link never resolves, e.g. [Clouds App]([https://example.com/x) — mkdocs
    # silently leaves it un-rendered instead of erroring, so the converter
    # must catch it.
    out, flags = convert_links("The [Clouds App]([https://example.com/x) provides:")
    assert any(
        f.section == "blocking" and "malformed" in f.message.lower() for f in flags
    )


def test_stale_internal_codelabs_link_flagged():
    # Real source cross-reference to the discarded CLaaT /codelabs/ site —
    # dead once migrated, must be flagged for a human to repoint.
    out, flags = convert_links(
        '<a href="/codelabs/azure-grail-lab0/index.html?index=..%2F..azure#5"'
        'target="_blank">two values</a> in a notepad session.'
    )
    assert any(
        f.section == "blocking" and "/codelabs/" in f.message for f in flags
    )


def test_multiline_anchor_text_converted():
    out, flags = convert_links('<a href="https://z.io/" target="_blank">Two\nlines</a>')
    assert "[Two\nlines](https://z.io/){target=\"_blank\"}" in out
