import re

_FENCE_RE = re.compile(r"^\s*```")


def reindent_lists(body: str) -> str:
    out = []
    in_fence = False
    for line in body.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent >= 3 and stripped:
            new_indent = max(4, (indent // 4) * 4)
            out.append(" " * new_indent + stripped)
        else:
            out.append(line)
    trailing = "\n" if body.endswith("\n") else ""
    return "\n".join(out) + trailing
