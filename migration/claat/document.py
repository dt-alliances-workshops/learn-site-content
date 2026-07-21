import pathlib
import re
from dataclasses import dataclass, field

from migration.claat.asides import convert_asides
from migration.claat.duration import strip_duration
from migration.claat.header import parse_header
from migration.claat.images import process_images
from migration.claat.links import convert_links
from migration.claat.lists import reindent_lists
from migration.claat.models import Flag

_STALE_FEEDBACK = ("workshops-content", "claat-mockup", "mailto:")
_H1_RE = re.compile(r"^#\s+(.*)$", re.MULTILINE)


@dataclass
class ConvertedDoc:
    markdown: str
    metadata: dict
    title: str
    total_minutes: int
    image_renames: dict
    flags: list = field(default_factory=list)


def _resolve_lines(markdown: str, flags: list[Flag]) -> None:
    lines = markdown.splitlines()
    # Per-locator search cursor: when several flags share the same locator
    # text (common with repeated boilerplate like "How this helps"), each
    # one must resolve to its own occurrence in document order rather than
    # all collapsing onto the first match.
    next_start: dict[str, int] = {}
    for f in flags:
        if not f.locator:
            continue
        start = next_start.get(f.locator, 0)
        for idx in range(start, len(lines)):
            if f.locator in lines[idx]:
                f.line = idx + 1
                next_start[f.locator] = idx + 1
                break
        else:
            # No occurrence at or after the cursor (fewer real occurrences
            # than flags, or locator only matches earlier in the file) —
            # fall back to the first match anywhere so the flag still gets
            # a usable pointer instead of being left unresolved.
            for idx, ln in enumerate(lines):
                if f.locator in ln:
                    f.line = idx + 1
                    break


def convert_document(
    readme_text: str, src_img_dir: pathlib.Path, labslug: str
) -> ConvertedDoc:
    meta, body = parse_header(readme_text)
    title_m = _H1_RE.search(body)
    title = title_m.group(1).strip() if title_m else labslug

    body, aside_flags = convert_asides(body)
    body, total = strip_duration(body)
    body, link_flags = convert_links(body)
    body = reindent_lists(body)
    body, renames, img_flags = process_images(body, src_img_dir, f"img/{labslug}")

    flags = aside_flags + link_flags + img_flags
    fb = meta.get("feedback_link", "")
    if any(s in fb for s in _STALE_FEEDBACK):
        flags.append(
            Flag(
                section="blocking",
                message=f"Stale Feedback Link ({fb}) — replace with the repo feedback link.",
            )
        )

    markdown = body.strip() + "\n"
    _resolve_lines(markdown, flags)
    return ConvertedDoc(
        markdown=markdown,
        metadata=meta,
        title=title,
        total_minutes=total,
        image_renames=renames,
        flags=flags,
    )
