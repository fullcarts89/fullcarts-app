import subprocess
from pathlib import Path
from typing import List, Union

PathLike = Union[str, Path]


def extract_text(pdf: PathLike) -> str:
    out = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        capture_output=True, text=True, check=True)
    return out.stdout


def render_pages(pdf: PathLike, out_dir: PathLike, first: int, last: int,
                 dpi: int = 100) -> List[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "page"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), "-f", str(first), "-l", str(last),
         str(pdf), str(prefix)],
        capture_output=True, check=True)
    return sorted(out_dir.glob("page*.png"))
