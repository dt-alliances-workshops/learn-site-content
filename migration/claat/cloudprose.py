from migration.claat.models import Flag

_KEYWORDS = (
    "azure portal", "aws console", "azure pass",
    "promo code", "subscription", "credentials",
)


def scan_cloud_prose(markdown: str) -> "Flag | None":
    low = markdown.lower()
    hit = next((k for k in _KEYWORDS if k in low), None)
    if hit is None:
        return None
    return Flag(
        section="env",
        message=f"References a cloud account/portal ('{hit}'); "
        "confirm docs-first wording (learner uses their own account).",
    )
