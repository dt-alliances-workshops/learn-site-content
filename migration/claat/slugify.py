import re


def slug_filename(name: str) -> str:
    """Normalize an image filename: fix spaces/zero-width/invalid chars in the
    stem, keep case in the stem, lowercase the extension."""
    dot = name.rfind(".")
    stem, ext = (name[:dot], name[dot + 1:]) if dot > 0 else (name, "")
    stem = stem.replace("​", "")           # drop zero-width spaces
    stem = re.sub(r"[^A-Za-z0-9.-]+", "-", stem)  # any run of other chars -> hyphen
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return f"{stem}.{ext.lower()}" if ext else stem


def slug_text(text: str) -> str:
    """Slugify an id/directory name to lowercase hyphen form."""
    out = re.sub(r"[^A-Za-z0-9]+", "-", text.strip()).strip("-").lower()
    return out


def natural_key(s: str) -> list:
    """Sort key so 'lab2' < 'lab10'."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]
