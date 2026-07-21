from dataclasses import dataclass


@dataclass
class Flag:
    section: str        # one of: blocking, screenshot, alt, judgment
    message: str
    locator: str = ""   # substring to locate in final markdown (for line resolution)
    line: int = 0
