from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vr_coloraccept.core import load_dataset, recalculate_metrics, image_zip_inventory, COND_ORDER


def main() -> None:
    dataset_path = ROOT / "data/raw/VR_Dataset_600rows.xlsx"
    image_zip = ROOT / "data/raw/VR_Image_dataset_final.zip"
    out_dir = ROOT / "outputs/tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset(dataset_path)
    calc = recalculate_metrics(df)
    inv = image_zip_inventory(image_zip)

    checks = []
    def add(name: str, passed: bool, details: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "details": details})

    add("600 rows", len(df) == 600, f"rows={len(df)}")
    add("100 scenes", df["scene_id"].nunique() == 100, f"scenes={df['scene_id'].nunique()}")
    counts = df.groupby("condition_id", observed=True).size().reindex(COND_ORDER)
    add("100 rows per condition", (counts == 100).all(), counts.to_dict().__str__())
    add("unique scene-condition keys", not df.duplicated(["scene_id", "condition_id"]).any(), "duplicates=" + str(df.duplicated(["scene_id", "condition_id"]).sum()))
    add("AAS in 1-7", df["AAS_1_7"].between(1, 7).all(), f"range=[{df['AAS_1_7'].min()}, {df['AAS_1_7'].max()}]")
    add("CFS in 1-7", df["CFS_1_7"].between(1, 7).all(), f"range=[{df['CFS_1_7'].min()}, {df['CFS_1_7'].max()}]")
    add("AAS ranks match", (calc["AAS_rank_recalc"] == calc["AAS_rank_within_scene"]).all(), f"mismatches={(calc['AAS_rank_recalc'] != calc['AAS_rank_within_scene']).sum()}")
    add("CFS ranks match", (calc["CFS_rank_recalc"] == calc["CFS_rank_within_scene"]).all(), f"mismatches={(calc['CFS_rank_recalc'] != calc['CFS_rank_within_scene']).sum()}")
    add("TI values match", (calc["TI_recalc"] == calc["TI_rank_gap"]).all(), f"mismatches={(calc['TI_recalc'] != calc['TI_rank_gap']).sum()}")
    add("Utility values match", (calc["Utility_recalc"] == calc["Dual_loop_score"].round(2)).all(), f"mismatches={(calc['Utility_recalc'] != calc['Dual_loop_score'].round(2)).sum()}")
    add("600 images", len(inv) == 600, f"images={len(inv)}")
    image_counts = inv.groupby("condition").size().reindex(COND_ORDER)
    add("100 images per condition", (image_counts == 100).all(), image_counts.to_dict().__str__())
    add("all images 1600x800", ((inv["width"] == 1600) & (inv["height"] == 800)).all(), f"nonmatching={((inv['width'] != 1600) | (inv['height'] != 800)).sum()}")
    add("unique image filenames", inv["filename"].is_unique, f"duplicate_names={inv['filename'].duplicated().sum()}")
    add("no byte-identical images", inv["sha256"].is_unique, f"duplicate_hashes={inv['sha256'].duplicated().sum()}")
    dataset_files = set(df["image_file"].astype(str))
    zip_files = set(inv["filename"].astype(str))
    add("dataset/image filename match", dataset_files == zip_files, f"missing_in_zip={len(dataset_files-zip_files)}, extra_in_zip={len(zip_files-dataset_files)}")

    check_df = pd.DataFrame(checks)
    check_df.to_csv(out_dir / "validation_report.csv", index=False)
    inv.to_csv(out_dir / "image_inventory.csv", index=False)
    if not check_df["passed"].all():
        print(check_df.to_string(index=False))
        raise SystemExit("Validation failed")
    print(check_df.to_string(index=False))
    print("\nAll validation checks passed.")

if __name__ == "__main__":
    main()
