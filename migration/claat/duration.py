import re

_DUR_RE = re.compile(r"^Duration:\s*(\d+)\s*$", re.MULTILINE)


def strip_duration(body: str) -> tuple[str, int]:
    total = 0

    def repl(m: "re.Match") -> str:
        nonlocal total
        n = int(m.group(1))
        total += n
        return f"<!-- Duration: {n} min -->"

    return _DUR_RE.sub(repl, body), total
