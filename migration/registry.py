import fnmatch
import pathlib
from dataclasses import dataclass, field

from migration.claat.header import parse_header
from migration.claat.slugify import natural_key


def parse_tags(meta: dict) -> list[str]:
    return [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]


@dataclass
class Workshop:
    name: str
    repo_name: str
    title: str
    selector_type: str  # "dir_glob" | "tag"
    selector: str
    tags: list[str] = field(default_factory=list)
    duration: str = "TBD"


WORKSHOPS: list[Workshop] = [
    Workshop("azure-grail", "enablement-azure-grail", "Azure Grail",
             "dir_glob", "azure-grail-lab*", ["azure", "grail", "kubernetes"], "2h"),
    Workshop("azure-aks-levelup", "enablement-azure-aks-levelup", "Azure AKS LevelUp",
             "dir_glob", "azure-aks-levelup-lab*", ["azure", "aks", "kubernetes"], "1.5h"),
    Workshop("azure-gen2", "enablement-azure-gen2", "Azure Gen2",
             "dir_glob", "azure-lab*", ["azure", "modernization"], "3h"),
    Workshop("aws-immersion-day", "enablement-aws-immersion-day", "AWS Immersion Day",
             "tag", "aws-immersion-day", ["aws"], "3h"),
    Workshop("aws-immersion-day-saas", "enablement-aws-immersion-day-saas",
             "AWS Immersion Day (SaaS)", "tag", "aws-immersion-day-saas", ["aws"], "3h"),
    Workshop("aws-serverless", "enablement-aws-serverless", "AWS Serverless Observability",
             "tag", "aws-immersion-day-serverless", ["aws", "serverless"], "1.5h"),
    Workshop("aws-selfpaced", "enablement-aws-selfpaced", "AWS Self-paced",
             "tag", "aws-selfpaced", ["aws"], "3h"),
]

_BY_NAME = {w.name: w for w in WORKSHOPS}


def get_workshop(name: str) -> Workshop:
    return _BY_NAME[name]


def is_excluded(dirname: str) -> bool:
    return dirname.endswith("-jp") or dirname.startswith("redhat101-") or dirname == "Unused"


def _lab_dirs(corpus_dir: pathlib.Path):
    for d in sorted(corpus_dir.iterdir(), key=lambda p: natural_key(p.name)):
        if not d.is_dir():
            continue
        if is_excluded(d.name):
            continue
        if not (d / "README.md").exists():
            continue
        yield d


def _matches(workshop: Workshop, d: pathlib.Path) -> bool:
    if workshop.selector_type == "dir_glob":
        return fnmatch.fnmatch(d.name, workshop.selector)
    meta, _ = parse_header((d / "README.md").read_text())
    return workshop.selector in parse_tags(meta)


def select_labs(workshop: Workshop, corpus_dir) -> list[pathlib.Path]:
    corpus_dir = pathlib.Path(corpus_dir)
    return [d for d in _lab_dirs(corpus_dir) if _matches(workshop, d)]


def find_orphans(corpus_dir) -> list[str]:
    corpus_dir = pathlib.Path(corpus_dir)
    claimed = set()
    for w in WORKSHOPS:
        claimed.update(d.name for d in select_labs(w, corpus_dir))
    return [d.name for d in _lab_dirs(corpus_dir) if d.name not in claimed]
