from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vr_coloraccept.core import load_dataset, recalculate_metrics


def test_dataset_and_metrics():
    df = load_dataset(ROOT / "data/raw/VR_Dataset_600rows.xlsx")
    assert len(df) == 600
    assert df["scene_id"].nunique() == 100
    calc = recalculate_metrics(df)
    assert np.allclose(calc["TI_recalc"], calc["TI_rank_gap"])
    assert np.allclose(calc["Utility_recalc"], calc["Dual_loop_score"].round(2))
