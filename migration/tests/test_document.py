import pathlib

from migration.claat.document import _resolve_lines, convert_document
from migration.claat.models import Flag

FIXROOT = pathlib.Path(__file__).parent / "fixtures" / "sample_claat"


def test_convert_document_end_to_end():
    text = (FIXROOT / "README.md").read_text()
    doc = convert_document(text, FIXROOT / "img", "lab0")
    # header lifted
    assert doc.metadata["id"] == "sample-lab"
    assert doc.title == "Sample Fixture Lab - One Of Each"
    # durations summed and removed from visible body
    assert doc.total_minutes == 8
    assert "Duration: 3\n" not in doc.markdown
    # aside converted
    assert "!!! tip" in doc.markdown
    assert "!!! warning" in doc.markdown
    # link converted
    assert '{target="_blank"}' in doc.markdown
    # image rewritten with prefix + slug
    assert "](img/lab0/pic-one.png)" in doc.markdown
    assert doc.image_renames["pic one.png"] == "pic-one.png"


def test_stale_feedback_link_flagged():
    text = (FIXROOT / "README.md").read_text()
    doc = convert_document(text, FIXROOT / "img", "lab0")
    assert any(
        f.section == "blocking" and "feedback" in f.message.lower() for f in doc.flags
    )


def test_flags_have_resolved_line_numbers():
    text = (FIXROOT / "README.md").read_text()
    doc = convert_document(text, FIXROOT / "img", "lab0")
    # at least one flag resolved to a real (non-zero) line
    assert any(f.line > 0 for f in doc.flags)


def test_resolve_lines_repeated_locator_resolves_to_distinct_lines():
    # Real Grail content repeats an identical aside opener ("How this helps")
    # many times in one doc. Each flag must resolve to its OWN occurrence,
    # not collapse onto the first match found in the file.
    markdown = "\n".join(
        [
            "line 1",
            "    How this helps",  # line 2 — first occurrence
            "line 3",
            "line 4",
            "    How this helps",  # line 5 — second occurrence
            "line 6",
            "    How this helps",  # line 7 — third occurrence
        ]
    )
    flags = [
        Flag(section="blocking", message="first", locator="How this helps"),
        Flag(section="blocking", message="second", locator="How this helps"),
        Flag(section="blocking", message="third", locator="How this helps"),
    ]
    _resolve_lines(markdown, flags)
    assert [f.line for f in flags] == [2, 5, 7]
