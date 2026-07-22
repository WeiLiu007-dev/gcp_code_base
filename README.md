# VR-ColorAccept Scene-Level Multi-Objective Evaluation Codebase

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21496862.svg)](https://doi.org/10.5281/zenodo.21496862)

This repository contains the data, code, validation outputs, statistical tables, and figures for the **secondary scene-level analysis** reported in the manuscript:

> *A Scene-Level Multi-Objective Evaluation Framework for Human-Centered Generative AI in Panoramic Virtual-Reality Color Design*

The retained archive comprises **600 matched scene-condition records** from **100 panoramic virtual-reality scenes** under six archived condition labels (C1-C6), together with **600 corresponding 1600 × 800 JPEG stimuli**.

- GitHub: <https://github.com/WeiLiu007-dev/gcp_code_base>
- Archived release (v1.1.0): <https://doi.org/10.5281/zenodo.21496862>
- License: MIT

## Evidence boundary

The codebase reproduces:

- dataset and image-archive integrity checks;
- within-scene AAS and CFS ranks, the Trade-off Index (TI), and supplementary utility;
- descriptive statistics and scene-level bootstrap confidence intervals;
- Friedman tests and Kendall's W;
- design-motivated C6-versus-comparator Wilcoxon signed-rank tests;
- Holm correction and rank-biserial effect sizes;
- utility-sensitivity analysis under six coefficient specifications;
- outcome-pattern and C6-difference diagnostics;
- exploratory image-feature correlations with BH-FDR correction; and
- the analytical content of Figures 1-4.

The codebase does **not** reconstruct the original participant-level rating protocol, validate AAS or CFS as psychometric scales, reproduce the generation procedures associated with C1-C6, or establish the causal or universal superiority of a condition or underlying model. AAS and CFS are retained study-specific scene-condition aggregates. The condition labels are archived comparison labels, not independently verified algorithm descriptions.

## Repository structure

```text
gcp_code_base/
├── data/
│   └── raw/
│       ├── VR_Dataset_600rows.xlsx
│       └── VR_Image_dataset_final.zip       # Git LFS
├── outputs/
│   ├── figures/
│   │   ├── Figure_1.png/.svg/.tiff
│   │   ├── Figure_2.png/.svg/.tiff
│   │   ├── Figure_3.png/.svg/.tiff
│   │   └── Figure_4.png/.svg/.tiff
│   └── tables/
│       ├── validation_report.csv
│       ├── image_inventory.csv
│       ├── table2_outcome_provenance.csv
│       ├── table3_descriptive_statistics.csv
│       ├── table4_friedman_tests.csv
│       ├── table5_wilcoxon_tests.csv
│       ├── table6_utility_sensitivity.csv
│       ├── table7_selected_correlations.csv
│       └── appendix_table_A1_evidence_provenance.csv
├── scripts/
│   ├── validate_dataset.py
│   ├── run_analysis.py
│   ├── generate_figures.py
│   ├── package_submission_figures.py
│   └── run_all.py
├── src/
│   └── vr_coloraccept/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
├── .gitattributes
├── .gitignore
├── CITATION.cff
├── config.yaml
├── environment.yml
├── LICENSE
├── README.md
├── requirements.txt
└── SHA256SUMS.txt
```

Running `scripts/run_analysis.py` also creates a `supplementary/` directory containing Supplementary Tables S1-S3.

## Obtain the repository and large image archive

The 600-image ZIP is stored with Git LFS. Install Git LFS before cloning so that the real archive is downloaded instead of an LFS pointer file.

```bash
git lfs install
git clone https://github.com/WeiLiu007-dev/gcp_code_base.git
cd gcp_code_base
git lfs pull
```

Alternatively, download the archived v1.1.0 release from Zenodo using the DOI above.

## Environment setup

### pip

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the pinned dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### conda

```bash
conda env create -f environment.yml
conda activate vr-coloraccept
```

## Reproduce the released analysis

Run the following commands from the repository root:

```bash
python scripts/validate_dataset.py
python scripts/run_analysis.py
python scripts/generate_figures.py
```

These commands perform the released reproducibility workflow:

1. Validate the dataset and image ZIP.
2. Recalculate within-scene AAS/CFS ranks, TI, and primary utility.
3. Generate the manuscript-aligned main tables and Appendix Table A1.
4. Generate Supplementary Tables S1-S3.
5. Regenerate Figures 1-4 in PNG and SVG formats.

The canonical 300-dpi TIFF files are already provided in `outputs/figures/`.

### Note about `run_all.py`

`scripts/run_all.py` additionally calls `scripts/package_submission_figures.py`. That final packaging helper expects source TIFF files under `submission/figures/`, which is not included in the current public repository tree. Therefore, use the three commands above to reproduce the released analytical outputs. This packaging limitation does not affect the statistical tables, supplementary CSV files, regenerated PNG/SVG figures, or the canonical TIFF files already stored in `outputs/figures/`.

## Metric definitions

Within each scene, AAS and CFS are ranked independently in descending order using average ranks for ties:

```text
TI = abs(AAS rank - CFS rank)
```

The archived supplementary utility is:

```text
U = 0.46*AAS + 0.46*CFS - 0.16*TI
```

TI is derived from AAS and CFS ranks and is not an independent outcome. Utility is also derived from AAS, CFS, and TI; it is a supplementary descriptive summary and should be interpreted alongside its component outcomes. Because C6 was archived as the condition intended to balance these same outcomes, its utility ranking is not an independent validation of C6.

## Generated outputs

### Main and appendix tables

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
```

### Supplementary tables created at runtime

```text
supplementary/Supplementary_Table_S1_outcome_pattern_diagnostics.csv
supplementary/Supplementary_Table_S2_C6_difference_diagnostics.csv
supplementary/Supplementary_Table_S3_full_correlations.csv
```

### Figures

```text
outputs/figures/Figure_1.png
outputs/figures/Figure_1.svg
outputs/figures/Figure_1.tiff
outputs/figures/Figure_2.png
outputs/figures/Figure_2.svg
outputs/figures/Figure_2.tiff
outputs/figures/Figure_3.png
outputs/figures/Figure_3.svg
outputs/figures/Figure_3.tiff
outputs/figures/Figure_4.png
outputs/figures/Figure_4.svg
outputs/figures/Figure_4.tiff
```

## Validation expectations

A successful validation confirms:

- 600 rows, 100 scenes, and six complete conditions;
- 100 records per condition and 600 unique scene-condition keys;
- AAS and CFS values within the intended 1-7 range;
- stored AAS/CFS ranks, TI, and utility match independent recalculation;
- 600 images, with 100 images per condition;
- all images are 1600 × 800 pixels;
- dataset filenames match image-ZIP filenames; and
- no byte-identical image duplicates are present.

## Reproducibility settings

- Python: 3.12
- Bootstrap resamples: 20,000
- Random seed: 2026
- Wilcoxon zero handling: `zero_method="wilcox"`
- Pairwise multiplicity correction: Holm within each outcome family
- Exploratory-correlation correction: Benjamini-Hochberg across all 44 tests

Exact package versions are pinned in `requirements.txt` and `environment.yml`; analytical parameters are stored in `config.yaml`.

## Tests

The core metric-recalculation test uses `pytest`, which is not part of the runtime dependency file. To run it:

```bash
pip install pytest
python -m pytest
```

## Figure alignment

`scripts/generate_figures.py` regenerates analytical PNG and SVG files. The TIFF files in `outputs/figures/` are the canonical 300-dpi journal exports. Small renderer-dependent PNG/SVG pixel differences do not indicate analytical differences.

## Checksum note

`SHA256SUMS.txt` was generated from the original complete packaging workspace and includes entries for local packaging files that are not present in the current public GitHub tree. It should therefore be treated as a provenance inventory rather than run as a blanket checksum-verification command against the current checkout.

## Citation

Please cite the archived software release:

> Liu, W., Chen, J., & Marites, R. (2026). *VR-ColorAccept Scene-Level Analysis Codebase* (Version 1.1.0). Zenodo. <https://doi.org/10.5281/zenodo.21496862>

Machine-readable citation metadata are provided in `CITATION.cff`. Cite the associated manuscript separately once its final bibliographic record is available.

## License

This repository is released under the MIT License. See `LICENSE` for details.
