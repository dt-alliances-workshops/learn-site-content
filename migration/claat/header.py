import re

_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z ]*):\s*(.*)$")


def parse_header(text: str) -> tuple[dict[str, str], str]:
    """Parse the leading bare `key: value` CLaaT header block.

    The block is the run of key:value lines at the very start of the file,
    terminated by the first blank line or the first line starting with '#'.
    """
    lines = text.splitlines()
    meta: dict[str, str] = {}
    i = 0
    for i, line in enumerate(lines):
        if line.strip() == "" or line.startswith("#"):
            break
        m = _KEY_RE.match(line)
        if not m:
            break
        key = m.group(1).strip().lower().replace(" ", "_")
        meta[key] = m.group(2).strip()
    else:
        i = len(lines)
    body = "\n".join(lines[i:]).lstrip("\n")
    return meta, body
