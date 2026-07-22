from __future__ import annotations
from pathlib import Path
import shutil
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "submission" / "figures"
DEST = ROOT / "outputs" / "figures"

EXPECTED = [f"Figure_{i}.tiff" for i in range(1, 5)]


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name in EXPECTED:
        src = SOURCE / name
        if not src.exists():
            raise FileNotFoundError(f"Missing canonical submission figure: {src}")
        with Image.open(src) as img:
            if img.mode != "RGB":
                raise ValueError(f"{name} must be RGB, found {img.mode}")
            dpi = img.info.get("dpi", (0, 0))
            if round(dpi[0]) != 300 or round(dpi[1]) != 300:
                raise ValueError(f"{name} must be 300 dpi, found {dpi}")
        shutil.copy2(src, DEST / name)
    print("Canonical journal TIFF figures copied to outputs/figures.")


if __name__ == "__main__":
    main()
