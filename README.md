# VR-ColorAccept Scene-Level Multi-Objective Evaluation Codebase

This repository reproduces the **secondary scene-level analysis** reported in the manuscript:

> *A scene-level multi-objective evaluation framework for human-centered generative AI in panoramic virtual-reality color design*

The retained archive contains 600 matched scene-condition records from 100 panoramic scenes under six archived condition labels (C1-C6), together with 600 corresponding 1600 x 800 JPEG stimuli.

## Evidence boundary

This codebase reproduces dataset and image validation, descriptive statistics, scene-level bootstrap confidence intervals, Friedman tests, Kendall's W, design-motivated C6-versus-comparator Wilcoxon tests, Holm correction, rank-biserial effects, utility-sensitivity analysis, outcome-pattern diagnostics, C6 difference diagnostics, exploratory image-feature correlations, and the analytical content of Figures 1-4.

It does **not** reconstruct the original participant-level rating protocol, validate AAS or CFS as psychometric scales, reproduce the generation procedures associated with C1-C6, or establish causal superiority of an underlying model. The condition labels are retained comparison labels, not independently verified algorithm descriptions.

## Repository structure

```text
GCP_VR_Codebase/
├── config.yaml
├── requirements.txt
├── environment.yml
├── README.md
├── LICENSE
├── CITATION.cff
├── data/raw/
│   ├── VR_Dataset_600rows.xlsx
│   └── VR_Image_dataset_final.zip
├── docs/
│   └── GCP_VR_Frontiers_Formatted_Final.docx
├── src/vr_coloraccept/
│   ├── __init__.py
│   └── core.py
├── scripts/
│   ├── validate_dataset.py
│   ├── run_analysis.py
│   ├── generate_figures.py
│   ├── package_submission_figures.py
│   └── run_all.py
├── outputs/
│   ├── tables/
│   └── figures/
├── supplementary/
├── submission/figures/
└── tests/
```

## Setup

### pip

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### conda

```bash
conda env create -f environment.yml
conda activate vr-coloraccept
```

## Run the complete pipeline

From the repository root:

```bash
python scripts/run_all.py
```

The pipeline performs:

1. Dataset and image-ZIP integrity checks.
2. Recalculation of within-scene AAS/CFS ranks, TI, and primary utility.
3. Manuscript Table 2 outcome-variable provenance file.
4. Manuscript Table 3 descriptive statistics with 20,000-resample scene-level bootstrap CIs.
5. Manuscript Table 4 Friedman tests and Kendall's W.
6. Manuscript Table 5 C6-versus-comparator Wilcoxon tests, Holm correction, and rank-biserial effects.
7. Manuscript Table 6 utility sensitivity under six coefficient specifications.
8. Manuscript Table 7 selected exploratory feature-outcome associations.
9. Appendix Table A1 evidence-provenance summary.
10. Supplementary Table S1 outcome-pattern diagnostics.
11. Supplementary Table S2 C6-versus-comparator difference diagnostics.
12. Supplementary Table S3 complete 44-test Spearman matrix with BH-FDR correction.
13. Figures 1-4 in regenerated PNG/SVG formats and canonical 300-dpi TIFF format.

## Metric definitions

Within each scene, AAS and CFS are ranked independently in descending order using average ranks for ties:

```text
TI = abs(AAS rank - CFS rank)
```

The archived supplementary utility is:

```text
U = 0.46*AAS + 0.46*CFS - 0.16*TI
```

TI is derived from AAS and CFS ranks and is not an independent outcome. Utility is supplementary and should be interpreted alongside AAS, CFS, and TI.

## Output files

```text
outputs/tables/validation_report.csv
outputs/tables/image_inventory.csv
outputs/tables/table2_outcome_provenance.csv
outputs/tables/table3_descriptive_statistics.csv
outputs/tables/table4_friedman_tests.csv
outputs/tables/table5_wilcoxon_tests.csv
outputs/tables/table6_utility_sensitivity.csv
outputs/tables/table7_selected_correlations.csv
outputs/tables/appendix_table_A1_evidence_provenance.csv
supplementary/Supplementary_Table_S1_outcome_pattern_diagnostics.csv
supplementary/Supplementary_Table_S2_C6_difference_diagnostics.csv
supplementary/Supplementary_Table_S3_full_correlations.csv
outputs/figures/Figure_1.png/.svg/.tiff
outputs/figures/Figure_2.png/.svg/.tiff
outputs/figures/Figure_3.png/.svg/.tiff
outputs/figures/Figure_4.png/.svg/.tiff
```

## Validation expectations

A successful run confirms:

- 600 rows, 100 scenes, and six complete conditions.
- 600 unique scene-condition keys.
- AAS and CFS values within 1-7.
- Stored AAS/CFS ranks, TI, and utility match recalculation.
- 600 images, 100 per condition, all 1600 x 800.
- Dataset filenames match image-ZIP filenames.
- No byte-identical image duplicates.

## Reproducibility settings

- Python 3.12
- Bootstrap resamples: 20,000
- Random seed: 2026
- Wilcoxon zero handling: `zero_method="wilcox"`
- Pairwise multiplicity correction: Holm within each outcome family
- Exploratory-correlation correction: Benjamini-Hochberg across all 44 tests

## Figure alignment

The TIFF files in `submission/figures/` are the canonical journal exports embedded in the manuscript. The pipeline regenerates analytical PNG/SVG figures and copies the canonical TIFF exports into `outputs/figures/`. Small renderer-dependent PNG/SVG pixel differences do not indicate analytical differences.

## Citation

Use `CITATION.cff` and cite the associated manuscript once its final bibliographic record is available.
