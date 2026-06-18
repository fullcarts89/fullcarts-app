import re
from typing import Dict, List, Any

_DIFF_RE = re.compile(r"(Beginner|Intermediate|Advanced)", re.IGNORECASE)


def _extract_title(text: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        despaced = re.sub(r"\s+", "", line).upper()
        if "RECREATIONGUIDE" in despaced:
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip()
    for line in lines:  # fallback: first non-empty line
        if line.strip():
            return line.strip()
    return "Untitled"


def _numbered_block(text: str) -> List[str]:
    # A bare integer on its own line starts a step; following non-empty lines
    # are its body until the next bare integer.
    steps: List[str] = []
    cur: List[str] = []
    for line in text.splitlines():
        if re.fullmatch(r"\s*\d+\s*", line):
            if cur:
                steps.append(" ".join(cur).strip())
            cur = []
        elif line.strip():
            cur.append(line.strip())
    if cur:
        steps.append(" ".join(cur).strip())
    return [s for s in steps if s]


def parse_manual_text(text: str) -> Dict[str, Any]:
    title = _extract_title(text)

    diff_m = _DIFF_RE.search(text)
    difficulty = diff_m.group(1) if diff_m else "unknown"

    filming = ""
    editing = ""
    parts = re.split(r"Part\s*1\s*[—-]\s*Filming", text, flags=re.IGNORECASE)
    if len(parts) > 1:
        rest = parts[1]
        edit_split = re.split(r"Part\s*2\s*[—-]\s*Editing[^\n]*", rest,
                              flags=re.IGNORECASE)
        filming = edit_split[0]
        editing = edit_split[1] if len(edit_split) > 1 else ""

    # Trim trailing reference sections so they don't pollute edit steps.
    editing = re.split(r"Official visual step-by-step", editing,
                       flags=re.IGNORECASE)[0]

    return {
        "title": title,
        "difficulty": difficulty,
        "editor": "CapCut" if "CapCut" in text else "unknown",
        "shot_on": "phone" if re.search(r"Shot on phone", text, re.I) else "unknown",
        "filming_steps": _numbered_block(filming),
        "edit_steps": _numbered_block(editing),
    }
