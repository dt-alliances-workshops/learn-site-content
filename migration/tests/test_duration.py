from migration.claat.duration import strip_duration


def test_strip_duration_removes_visible_line_and_sums():
    body = "## A\nDuration: 3\n\ntext\n\n## B\nDuration: 5\n\nmore\n"
    out, total = strip_duration(body)
    assert total == 8
    assert "Duration: 3" not in out.replace("<!-- Duration: 3 min -->", "")
    assert "<!-- Duration: 3 min -->" in out
    assert "<!-- Duration: 5 min -->" in out


def test_strip_duration_no_durations():
    out, total = strip_duration("## A\n\ntext\n")
    assert total == 0
    assert out == "## A\n\ntext\n"
