import re

from migration.claat.models import Flag

_TARGET_RE = re.compile(
    r'<a\s+href="([^"]*)"[^>]*target="_blank"[^>]*>(.*?)</a>', re.DOTALL
)
_PLAIN_RE = re.compile(r'<a\s+href="([^"]*)"\s*>(.*?)</a>', re.DOTALL)
_EMPTY_TARGET_RE = re.compile(r"\]\(\s*\)")


def convert_links(body: str) -> tuple[str, list[Flag]]:
    body = _TARGET_RE.sub(r'[\2](\1){target="_blank"}', body)
    body = _PLAIN_RE.sub(r"[\2](\1)", body)
    flags: list[Flag] = []
    for m in _EMPTY_TARGET_RE.finditer(body):
        flags.append(
            Flag(
                section="blocking",
                message="Markdown link with empty target — fix or remove.",
                locator=body[max(0, m.start() - 20): m.start()].splitlines()[-1]
                if body[:m.start()].strip() else "",
            )
        )
    return body, flags
