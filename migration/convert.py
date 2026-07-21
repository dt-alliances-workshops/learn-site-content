import argparse
import json
import pathlib
import shutil
import sys
from dataclasses import asdict

from migration.claat.document import convert_document
from migration.claat.slugify import natural_key, slug_text


def _lab_dirs(src_family_dir: pathlib.Path) -> list[pathlib.Path]:
    dirs = [p for p in src_family_dir.iterdir() if p.is_dir()]
    return sorted(dirs, key=lambda p: natural_key(p.name))


def convert_family(
    src_family_dir: pathlib.Path,
    out_repo_dir: pathlib.Path,
    strip_prefix: str = "",
) -> dict:
    src_family_dir = pathlib.Path(src_family_dir)
    out_repo_dir = pathlib.Path(out_repo_dir)
    docs = out_repo_dir / "docs"
    labs_log = []
    nav_lines = ['  - "Welcome": index.md']

    for i, d in enumerate(_lab_dirs(src_family_dir), start=1):
        name = d.name
        labslug = slug_text(name[len(strip_prefix):] if name.startswith(strip_prefix) else name)
        doc = convert_document((d / "README.md").read_text(), d / "img", labslug)
        page = f"{i}-{labslug}.md"
        (docs / page).write_text(doc.markdown)

        img_out = docs / "img" / labslug
        img_out.mkdir(parents=True, exist_ok=True)
        for orig, new in doc.image_renames.items():
            src_img = d / "img" / orig
            if src_img.exists():
                shutil.copyfile(src_img, img_out / new)

        flags = [asdict_flag(f) for f in doc.flags]
        flags.append({"section": "screenshot", "message":
                      f"Run this lab and verify its {len(doc.image_renames)} "
                      f"screenshots are current (technical-accuracy gate).",
                      "locator": "", "line": 0})
        flags.append({"section": "judgment", "message":
                      "Confirm this lab still belongs in the migrated workshop.",
                      "locator": "", "line": 0})

        nav_lines.append(f'  - "{i}. {doc.title}": {page}')
        labs_log.append({
            "labslug": labslug, "source": name, "page": f"docs/{page}",
            "title": doc.title, "total_minutes": doc.total_minutes,
            "image_count": len(doc.image_renames), "flags": flags,
            "metadata": doc.metadata,
        })

    # inject nav
    mk = out_repo_dir / "mkdocs.yaml"
    mk.write_text(mk.read_text().replace("# NAV_PLACEHOLDER", "\n".join(nav_lines)))

    log = {"repo": out_repo_dir.name, "labs": labs_log}
    (out_repo_dir / "transform_log.json").write_text(json.dumps(log, indent=2))
    return log


def asdict_flag(f) -> dict:
    return {"section": f.section, "message": f.message, "locator": f.locator, "line": f.line}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Convert a CLaaT workshop family.")
    ap.add_argument("src_family_dir")
    ap.add_argument("out_repo_dir")
    ap.add_argument("--strip-prefix", default="")
    args = ap.parse_args(argv)
    log = convert_family(args.src_family_dir, args.out_repo_dir, args.strip_prefix)
    print(f"Converted {len(log['labs'])} labs into {args.out_repo_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
