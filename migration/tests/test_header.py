from migration.claat.header import parse_header


HEADER = (
    "summary: Dynatrace Workshop on Azure Grail Introduction\n"
    "id: azure-grail-lab0\n"
    "categories: modernization,kubernetes,grail,all\n"
    "tags: azure, grail\n"
    "status: Published\n"
    "authors: Jay Gurbani\n"
    "Feedback Link: https://example.com/fb\n"
    "\n"
    "# Azure Grail Workshop Lab 0 - Setup\n"
    "\n"
    "Body starts here.\n"
)


def test_parse_header_extracts_all_keys():
    meta, body = parse_header(HEADER)
    assert meta["id"] == "azure-grail-lab0"
    assert meta["summary"] == "Dynatrace Workshop on Azure Grail Introduction"
    assert meta["feedback_link"] == "https://example.com/fb"


def test_parse_header_body_excludes_header():
    meta, body = parse_header(HEADER)
    assert body.startswith("# Azure Grail Workshop Lab 0 - Setup")
    assert "summary:" not in body


def test_parse_header_does_not_consume_duration_lines():
    # A body 'Duration: 3' line must NOT be swallowed as a header key.
    text = "id: x\n\n# Title\n\n## Step\nDuration: 3\n\nText\n"
    meta, body = parse_header(text)
    assert "duration" not in meta
    assert "Duration: 3" in body
