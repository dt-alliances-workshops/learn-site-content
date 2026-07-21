import re

from migration.claat.models import Flag

_TARGET_RE = re.compile(
    r'<a\s+href="([^"]*)"[^>]*target="_blank"[^>]*>(.*?)</a>', re.DOTALL
)
_PLAIN_RE = re.compile(r'<a\s+href="([^"]*)"\s*>(.*?)</a>', re.DOTALL)

# Each entry: (pattern, message). All are genuine "broken/stale link" cases
# per the transform spec (rule 15) — detected and flagged for a human to fix,
# never auto-repaired since the correct destination isn't derivable.
_LINK_ISSUES = [
    (
        re.compile(r"\]\(\s*\)"),
        "Markdown link with empty target — fix or remove.",
    ),
    (
        re.compile(r"\]\(\["),
        "Malformed markdown link (destination starts with a stray '[') — "
        "fix the link syntax.",
    ),
    (
        re.compile(r"\]\(/codelabs/"),
        "Stale internal CLaaT link (points at the discarded /codelabs/ "
        "site) — repoint to the migrated lab page.",
    ),
]


def _locator(body: str, start: int) -> str:
    if not body[:start].strip():
        return ""
    return body[max(0, start - 20): start].splitlines()[-1]


def convert_links(body: str) -> tuple[str, list[Flag]]:
    body = _TARGET_RE.sub(r'[\2](\1){target="_blank"}', body)
    body = _PLAIN_RE.sub(r"[\2](\1)", body)
    flags: list[Flag] = []
    for pattern, message in _LINK_ISSUES:
        for m in pattern.finditer(body):
            flags.append(
                Flag(section="blocking", message=message, locator=_locator(body, m.start())),
            )
    return body, flags
