import pathlib

from migration.claat.document import convert_document

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
