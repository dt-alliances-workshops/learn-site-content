import argparse
import json
import pathlib
import shutil
import sys

from migration.claat.cloudprose import scan_cloud_prose
from migration.claat.document import convert_document
from migration.claat.slugify import slug_text
from migration.registry import Workshop, get_workshop, select_labs


def asdict_flag(f) -> dict:
    return {"section": f.section, "message": f.message, "locator": f.locator, "line": f.line}


def _convert_lab(lab_dir: pathlib.Path, index: int, docs: pathlib.Path) -> tuple[dict, str]:
    name = lab_dir.name
    labslug = slug_text(name)
    doc = convert_document((lab_dir / "README.md").read_text(), lab_dir / "img", labslug)
    page = f"{index}-{labslug}.md"
    (docs / page).write_text(doc.markdown)

    img_out = docs / "img" / labslug
    img_out.mkdir(parents=True, exist_ok=True)
    for orig, new in doc.image_renames.items():
        src_img = lab_dir / "img" / orig
        if src_img.exists():
            shutil.copyfile(src_img, img_out / new)

    flags = [asdict_flag(f) for f in doc.flags]
    env_flag = scan_cloud_prose(doc.markdown)
    if env_flag is not None:
        flags.append(asdict_flag(env_flag))
    flags.append({"section": "screenshot", "message":
                  f"Run this lab and verify its {len(doc.image_renames)} "
                  f"screenshots are current (technical-accuracy gate).",
                  "locator": "", "line": 0})
    flags.append({"section": "judgment", "message":
                  "Confirm this lab still belongs in the migrated workshop.",
                  "locator": "", "line": 0})

    lab_log = {
        "labslug": labslug, "source": name, "page": f"docs/{page}",
        "id": doc.metadata.get("id", ""),
        "title": doc.title, "total_minutes": doc.total_minutes,
        "image_count": len(doc.image_renames), "flags": flags,
        "metadata": doc.metadata,
    }
    safe_title = doc.title.replace("\\", "\\\\").replace('"', '\\"')
    nav_line = f'  - "{index}. {safe_title}": {page}'
    return lab_log, nav_line


def convert_workshop(workshop: Workshop, corpus_dir, out_repo_dir) -> dict:
    out_repo_dir = pathlib.Path(out_repo_dir)
    docs = out_repo_dir / "docs"
    labs_log = []
    nav_lines = ['  - "Welcome": index.md']

    for i, lab_dir in enumerate(select_labs(workshop, corpus_dir), start=1):
        lab_log, nav_line = _convert_lab(lab_dir, i, docs)
        labs_log.append(lab_log)
        nav_lines.append(nav_line)

    mk = out_repo_dir / "mkdocs.yaml"
    mk.write_text(mk.read_text().replace("# NAV_PLACEHOLDER", "\n".join(nav_lines)))

    log = {"repo": out_repo_dir.name, "workshop": workshop.name, "labs": labs_log}
    (out_repo_dir / "transform_log.json").write_text(json.dumps(log, indent=2))
    return log


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Convert a CLaaT workshop by registry name.")
    ap.add_argument("--workshop", required=True, help="registry workshop name")
    ap.add_argument("--out", required=True, help="output repo dir (already scaffolded)")
    ap.add_argument("--corpus", default="workshop-markdown")
    args = ap.parse_args(argv)
    log = convert_workshop(get_workshop(args.workshop), args.corpus, args.out)
    print(f"Converted {len(log['labs'])} labs into {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
