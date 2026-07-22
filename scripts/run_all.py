from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for script in ["validate_dataset.py", "run_analysis.py", "generate_figures.py", "package_submission_figures.py"]:
    print(f"\n=== Running {script} ===")
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)
print("\nPipeline completed successfully.")
