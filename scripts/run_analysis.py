from __future__ import annotations
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vr_coloraccept.core import (
    load_dataset, outcome_provenance_table, descriptive_table, friedman_table,
    wilcoxon_table, sensitivity_table, correlation_table,
    outcome_pattern_diagnostics, c6_difference_diagnostics,
    evidence_provenance_table,
)


def main() -> None:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    df = load_dataset(ROOT / "data/raw/VR_Dataset_600rows.xlsx")
    out = ROOT / "outputs/tables"
    supp = ROOT / "supplementary"
    out.mkdir(parents=True, exist_ok=True)
    supp.mkdir(parents=True, exist_ok=True)

    outcome_provenance_table().to_csv(out / "table2_outcome_provenance.csv", index=False)
    descriptive_table(df, config["bootstrap_resamples"], config["random_seed"]).to_csv(out / "table3_descriptive_statistics.csv", index=False)
    friedman_table(df).to_csv(out / "table4_friedman_tests.csv", index=False)
    wilcoxon_table(df).to_csv(out / "table5_wilcoxon_tests.csv", index=False)
    sensitivity_table(df, config["sensitivity_specs"]).to_csv(out / "table6_utility_sensitivity.csv", index=False)

    full_corr = correlation_table(df)
    full_corr.to_csv(supp / "Supplementary_Table_S3_full_correlations.csv", index=False)
    selected = [("AAS", "colorfulness"), ("CFS", "dark_pixel_ratio"), ("CFS", "high_saturation_ratio")]
    full_corr.set_index(["Outcome", "Descriptor"]).loc[selected].reset_index().to_csv(out / "table7_selected_correlations.csv", index=False)

    outcome_pattern_diagnostics(df).to_csv(supp / "Supplementary_Table_S1_outcome_pattern_diagnostics.csv", index=False)
    c6_difference_diagnostics(df).to_csv(supp / "Supplementary_Table_S2_C6_difference_diagnostics.csv", index=False)
    evidence_provenance_table().to_csv(out / "appendix_table_A1_evidence_provenance.csv", index=False)
    print("Corrected manuscript-aligned tables created in outputs/tables and supplementary/.")

if __name__ == "__main__":
    main()
