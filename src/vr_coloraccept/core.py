from __future__ import annotations

from pathlib import Path
from typing import Iterable
import hashlib
import zipfile
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pandas as pd
from PIL import Image
from scipy import stats
from statsmodels.stats.multitest import multipletests

MAIN_SHEET = "Main_Dataset"
COND_ORDER = ["C1", "C2", "C3", "C4", "C5", "C6"]
OUTCOME_MAP = {
    "AAS": "AAS_1_7",
    "CFS": "CFS_1_7",
    "TI": "TI_rank_gap",
    "Dual utility": "Dual_loop_score",
}
DESCRIPTORS = [
    "mean_brightness", "mean_saturation", "luminance_contrast",
    "colorfulness", "hue_diversity", "dark_pixel_ratio",
    "high_saturation_ratio", "edge_density", "visual_complexity_index",
    "aesthetic_balance_index", "comfort_stability_index",
]


def load_dataset(path: str | Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=MAIN_SHEET)
    df["condition_id"] = pd.Categorical(df["condition_id"], COND_ORDER, ordered=True)
    return df.sort_values(["scene_id", "condition_id"]).reset_index(drop=True)


def descending_average_rank(values: pd.Series) -> pd.Series:
    return values.rank(method="average", ascending=False)


def recalculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["AAS_rank_recalc"] = out.groupby("scene_id", observed=True)["AAS_1_7"].transform(descending_average_rank)
    out["CFS_rank_recalc"] = out.groupby("scene_id", observed=True)["CFS_1_7"].transform(descending_average_rank)
    out["TI_recalc"] = (out["AAS_rank_recalc"] - out["CFS_rank_recalc"]).abs()
    raw_utility = 0.46 * out["AAS_1_7"] + 0.46 * out["CFS_1_7"] - 0.16 * out["TI_recalc"]
    out["Utility_recalc"] = raw_utility.map(lambda x: float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)))
    return out


def bootstrap_mean_ci(values: np.ndarray, n_resamples: int = 20000, seed: int = 2026) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(n_resamples, dtype=float)
    batch = 1000
    for start in range(0, n_resamples, batch):
        stop = min(start + batch, n_resamples)
        idx = rng.integers(0, n, size=(stop - start, n))
        means[start:stop] = values[idx].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return float(low), float(high)


def descriptive_table(df: pd.DataFrame, n_resamples: int = 20000, seed: int = 2026) -> pd.DataFrame:
    rows = []
    for cond in COND_ORDER:
        sub = df[df["condition_id"] == cond]
        row = {"Condition": cond}
        for label, col in OUTCOME_MAP.items():
            vals = sub[col].to_numpy(float)
            lo, hi = bootstrap_mean_ci(vals, n_resamples, seed)
            row[f"{label} mean"] = vals.mean()
            row[f"{label} SD"] = vals.std(ddof=1)
            row[f"{label} CI low"] = lo
            row[f"{label} CI high"] = hi
        rows.append(row)
    return pd.DataFrame(rows)


def friedman_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, col in OUTCOME_MAP.items():
        wide = df.pivot(index="scene_id", columns="condition_id", values=col)[COND_ORDER]
        stat, p = stats.friedmanchisquare(*[wide[c].to_numpy() for c in COND_ORDER])
        n, k = wide.shape
        kendalls_w = stat / (n * (k - 1))
        rows.append({"Outcome": label, "Friedman chi-square": stat, "df": k - 1, "p": p, "Kendall W": kendalls_w})
    return pd.DataFrame(rows)


def rank_biserial(diff: np.ndarray) -> float:
    diff = diff[diff != 0]
    if len(diff) == 0:
        return np.nan
    ranks = stats.rankdata(np.abs(diff), method="average")
    pos = ranks[diff > 0].sum()
    neg = ranks[diff < 0].sum()
    return float((pos - neg) / (pos + neg))


def wilcoxon_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, col in OUTCOME_MAP.items():
        wide = df.pivot(index="scene_id", columns="condition_id", values=col)[COND_ORDER]
        raw_p = []
        temp = []
        for comp in COND_ORDER[:-1]:
            diff = (wide["C6"] - wide[comp]).to_numpy(float)
            nonzero = diff[diff != 0]
            result = stats.wilcoxon(nonzero, zero_method="wilcox", alternative="two-sided", method="auto")
            raw_p.append(result.pvalue)
            temp.append({
                "Outcome": label,
                "Comparison": f"C6 vs {comp}",
                "Mean difference": diff.mean(),
                "W": result.statistic,
                "Raw p": result.pvalue,
                "Rank-biserial r": rank_biserial(diff),
                "Non-zero n": len(nonzero),
            })
        adjusted = multipletests(raw_p, method="holm")[1]
        for record, adj in zip(temp, adjusted):
            record["Holm-adjusted p"] = adj
            rows.append(record)
    return pd.DataFrame(rows)


def sensitivity_table(df: pd.DataFrame, specs: dict[str, Iterable[float]]) -> pd.DataFrame:
    rows = []
    for name, weights in specs.items():
        wa, wc, pt = [float(x) for x in weights]
        if name.lower() == "primary":
            score = df["Dual_loop_score"].astype(float)
        else:
            score = wa * df["AAS_1_7"] + wc * df["CFS_1_7"] - pt * df["TI_rank_gap"]
        temp = df[["scene_id", "condition_id"]].copy()
        temp["score"] = score
        means = temp.groupby("condition_id", observed=True)["score"].mean().reindex(COND_ORDER)
        leader = str(means.idxmax())
        wide = temp.pivot(index="scene_id", columns="condition_id", values="score")[COND_ORDER]
        c6 = wide["C6"]
        scenes_led_or_tied = int((c6 >= wide.max(axis=1) - 1e-12).sum())
        rows.append({
            "Specification": name,
            "AAS weight": wa,
            "CFS weight": wc,
            "TI penalty": pt,
            "Leading condition": leader,
            "Leading mean": means.max(),
            "Scenes led or tied by C6": scenes_led_or_tied,
        })
    return pd.DataFrame(rows)


def correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome_label, outcome_col in OUTCOME_MAP.items():
        for descriptor in DESCRIPTORS:
            rho, p = stats.spearmanr(df[descriptor], df[outcome_col], nan_policy="omit")
            rows.append({
                "Outcome": outcome_label,
                "Descriptor": descriptor,
                "Spearman rho": rho,
                "Raw p": p,
                "N": int(df[[descriptor, outcome_col]].dropna().shape[0]),
            })
    out = pd.DataFrame(rows)
    out["BH-FDR q"] = multipletests(out["Raw p"].to_numpy(), method="fdr_bh")[1]
    return out



def outcome_provenance_table() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Variable": "Aesthetic Acceptance Score (AAS)",
            "Archived meaning": "Study-specific aggregate representing favorable aesthetic response to each scene-condition output",
            "Scale": "1-7",
            "Higher-value direction": "Higher values indicate more favorable archived aesthetic acceptance",
            "Known components": "Beauty, preference, visual harmony or coherence, immersion compatibility, and revisit intention were listed in the retained documentation",
            "Unavailable information": "Exact item wording, response anchors, number of items, item weights, aggregation rule, missing-item handling, reliability, validity, and participant-level responses",
        },
        {
            "Variable": "Cognitive Feedback Score (CFS)",
            "Archived meaning": "Study-specific aggregate representing favorable cognitive and experiential response to each scene-condition output",
            "Scale": "1-7",
            "Higher-value direction": "Higher values indicate more favorable archived cognitive-feedback outcomes",
            "Known components": "Attention, visual comfort, emotional valence, cognitive load, fatigue, and discomfort were listed in the retained documentation",
            "Unavailable information": "Exact item wording, response anchors, reverse-coding procedure, number of items, item weights, aggregation rule, missing-item handling, reliability, validity, and participant-level responses",
        },
    ])


def outcome_pattern_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    wide_aas = df.pivot(index="scene_id", columns="condition_id", values="AAS_1_7")[COND_ORDER]
    wide_cfs = df.pivot(index="scene_id", columns="condition_id", values="CFS_1_7")[COND_ORDER]
    wide_ti = df.pivot(index="scene_id", columns="condition_id", values="TI_rank_gap")[COND_ORDER]
    rows = []
    metrics = [
        ("Unique AAS values", [int(df[df["condition_id"] == c]["AAS_1_7"].nunique()) for c in COND_ORDER]),
        ("Unique CFS values", [int(df[df["condition_id"] == c]["CFS_1_7"].nunique()) for c in COND_ORDER]),
        ("Highest frequency of any repeated AAS value, n", [int(df[df["condition_id"] == c]["AAS_1_7"].value_counts().max()) for c in COND_ORDER]),
        ("Highest frequency of any repeated CFS value, n", [int(df[df["condition_id"] == c]["CFS_1_7"].value_counts().max()) for c in COND_ORDER]),
        ("Scenes ranked first for AAS", [int((wide_aas.rank(axis=1, method="average", ascending=False)[c] == 1).sum()) for c in COND_ORDER]),
        ("Scenes ranked first for CFS", [int((wide_cfs.rank(axis=1, method="average", ascending=False)[c] == 1).sum()) for c in COND_ORDER]),
        ("Scenes with lowest or tied-lowest TI", [int((wide_ti[c] == wide_ti.min(axis=1)).sum()) for c in COND_ORDER]),
    ]
    for name, vals in metrics:
        row={"Diagnostic":name}
        row.update(dict(zip(COND_ORDER, vals)))
        rows.append(row)
    return pd.DataFrame(rows)


def c6_difference_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for label, col in OUTCOME_MAP.items():
        wide=df.pivot(index="scene_id", columns="condition_id", values=col)[COND_ORDER]
        for comp in COND_ORDER[:-1]:
            diff=(wide["C6"]-wide[comp]).to_numpy(float)
            rows.append({
                "Outcome":label,
                "Comparison":f"C6 vs {comp}",
                "Zero differences":int((diff==0).sum()),
                "Positive differences":int((diff>0).sum()),
                "Negative differences":int((diff<0).sum()),
            })
    return pd.DataFrame(rows)


def evidence_provenance_table() -> pd.DataFrame:
    return pd.DataFrame([
        ["Scene-condition coverage", "Verified", "600 unique records; 100 scenes x 6 conditions; no missing combinations."],
        ["Stimulus naming and dimensions", "Verified", "600 JPEG files; consistent Scene###_C# naming; 1600 x 800 pixels."],
        ["AAS and CFS aggregates", "Verified as stored variables", "Values and ranges were checked; item-level construction was unavailable."],
        ["Within-scene ranks and TI", "Verified", "Average ranks for ties; all stored TI values matched recalculation."],
        ["Dual utility", "Verified as stored formula", "Values matched 0.46(AAS)+0.46(CFS)-0.16(TI); coefficient origin unavailable."],
        ["Condition labels C1-C6", "Partially documented", "Labels and intended roles were retained; executable generation evidence was unavailable."],
        ["Participant protocol", "Unavailable", "No individual responses, allocation schedule, demographics, exclusions, or exposure logs."],
        ["Original ethics documentation", "Unavailable", "Approval/exemption identifier and consent documentation were not included in the retained archive."],
        ["Generation code and checkpoints", "Unavailable", "No executable generator, model checkpoint, training log, seed record, or inference history was retained."],
        ["Original collection dates and personnel", "Unavailable", "The dates and identities associated with original collection and aggregation were not preserved."],
        ["Current secondary-analysis code", "Available", "Validation, statistical analysis, sensitivity analysis, diagnostics, correlations, and figure generation are reproducible."],
    ], columns=["Evidence component", "Status", "Basis and limitation"])


def image_zip_inventory(zip_path: str | Path) -> pd.DataFrame:
    records = []
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            with zf.open(info) as f:
                data = f.read()
            with Image.open(__import__("io").BytesIO(data)) as im:
                width, height = im.size
                mode = im.mode
            filename = Path(info.filename).name
            condition = Path(info.filename).parent.name
            records.append({
                "zip_path": info.filename,
                "filename": filename,
                "condition": condition,
                "width": width,
                "height": height,
                "mode": mode,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": info.file_size,
            })
    return pd.DataFrame(records)
