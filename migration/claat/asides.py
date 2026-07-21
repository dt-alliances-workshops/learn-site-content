import re

from migration.claat.models import Flag

_ASIDE_RE = re.compile(
    r'<aside\s+class="(positive|negative)"\s*>(.*?)</aside>',
    re.DOTALL,
)
_ADMONITION = {"positive": "tip", "negative": "warning"}


def convert_asides(body: str) -> tuple[str, list[Flag]]:
    flags: list[Flag] = []

    def repl(m: "re.Match") -> str:
        kind = _ADMONITION[m.group(1)]
        inner = m.group(2).strip("\n")
        # Indent every line by 4 spaces (blank lines stay blank).
        indented = "\n".join(
            ("    " + ln) if ln.strip() else "" for ln in inner.splitlines()
        )
        has_image = "![" in inner
        multi_para = "\n\n" in inner.strip()
        nested = "<aside" in inner
        if has_image or multi_para or nested:
            snippet = inner.strip().splitlines()[0][:50] if inner.strip() else ""
            flags.append(
                Flag(
                    section="blocking",
                    message="Auto-converted aside with images/multiple paragraphs; "
                    "verify admonition body renders correctly.",
                    locator=snippet,
                )
            )
        return f"!!! {kind}\n{indented}"

    return _ASIDE_RE.sub(repl, body), flags
