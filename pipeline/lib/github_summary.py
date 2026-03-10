"""Write markdown tables to GitHub Actions step summary."""
import os
from typing import Dict, List, Optional

from pipeline.lib.logging_setup import get_logger

log = get_logger("github_summary")


def write_summary(
    title: str,
    rows: List[Dict[str, str]],
    stats: Optional[Dict[str, int]] = None,
) -> None:
    """Append a markdown summary to $GITHUB_STEP_SUMMARY.

    Falls back to logging when not running in GitHub Actions.
    """
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    lines = []

    lines.append(f"### {title}\n")

    if stats:
        for label, value in stats.items():
            lines.append(f"- **{label}**: {value}")
        lines.append("")

    if rows:
        headers = list(rows[0].keys())
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows[:50]:  # cap at 50 rows to avoid huge summaries
            cells = [str(row.get(h, "")) for h in headers]
            lines.append("| " + " | ".join(cells) + " |")
        if len(rows) > 50:
            lines.append(f"\n*... and {len(rows) - 50} more rows*")
    else:
        lines.append("*No items to display.*")

    text = "\n".join(lines) + "\n"

    if summary_path:
        with open(summary_path, "a") as f:
            f.write(text)
    else:
        log.info("GitHub summary (local):\n%s", text)
