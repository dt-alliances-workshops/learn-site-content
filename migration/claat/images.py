import pathlib
import re

from migration.claat.models import Flag
from migration.claat.slugify import slug_filename

_IMG_RE = re.compile(r"!\[[^\]]*\]\(img/([^)]+)\)")


def _alt_from_slug(slug: str) -> str:
    stem = slug.rsplit(".", 1)[0]
    return stem.replace("-", " ").replace("_", " ").strip()


def process_images(
    body: str, src_img_dir: pathlib.Path, dest_prefix: str
) -> tuple[str, dict[str, str], list[Flag]]:
    renames: dict[str, str] = {}
    flags: list[Flag] = []

    def repl(m: "re.Match") -> str:
        orig = m.group(1)
        new = slug_filename(orig)
        renames[orig] = new
        alt = _alt_from_slug(new)
        if not (src_img_dir / orig).exists():
            flags.append(
                Flag(
                    section="blocking",
                    message=f"Referenced image not found on disk: img/{orig}",
                    locator=f"{dest_prefix}/{new}",
                )
            )
        flags.append(
            Flag(
                section="alt",
                message=f"Alt text auto-derived ('{alt}') — confirm it reads sensibly.",
                locator=f"{dest_prefix}/{new}",
            )
        )
        return f"![{alt}]({dest_prefix}/{new})"

    return _IMG_RE.sub(repl, body), renames, flags
