from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vr_coloraccept.core import load_dataset, descriptive_table, COND_ORDER

LABELS = ["C1 Original", "C2 Rule-based", "C3 Generative", "C4 Aesthetic-focused", "C5 Cognitive-focused", "C6 Dual-objective"]


def save(fig, name: str) -> None:
    out = ROOT / "outputs/figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(out / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = load_dataset(ROOT / "data/raw/VR_Dataset_600rows.xlsx")
    means = df.groupby("condition_id", observed=True)[["AAS_1_7", "CFS_1_7", "TI_rank_gap", "Dual_loop_score"]].mean().reindex(COND_ORDER)

    # Figure 1
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    im = ax.imshow(means.to_numpy(), aspect="auto")
    ax.set_xticks(np.arange(4), ["AAS", "CFS", "TI", "Dual utility"])
    ax.set_yticks(np.arange(6), LABELS)
    for i in range(6):
        for j in range(4):
            ax.text(j, i, f"{means.iloc[i, j]:.3f}", ha="center", va="center")
    ax.set_title("Condition means across core outcomes")
    cbar = fig.colorbar(im, ax=ax); cbar.set_label("Mean value")
    ax.set_xlabel("AAS, CFS, and utility: higher is better; TI: lower is better")
    fig.tight_layout(); save(fig, "Figure_1")

    # Figure 2
    desc = descriptive_table(df, n_resamples=20000, seed=2026).set_index("Condition").reindex(COND_ORDER)
    fig, ax = plt.subplots(figsize=(8.6, 5.8))
    x = np.arange(6)
    styles = [("AAS", "AAS mean", "AAS CI low", "AAS CI high", "o-"), ("CFS", "CFS mean", "CFS CI low", "CFS CI high", "s--"), ("Dual utility", "Dual utility mean", "Dual utility CI low", "Dual utility CI high", "D-.")]
    for label, m, lo, hi, fmt in styles:
        y = desc[m].to_numpy(); err = np.vstack([y-desc[lo].to_numpy(), desc[hi].to_numpy()-y])
        ax.errorbar(x, y, yerr=err, fmt=fmt, capsize=3, label=label)
    ax.set_xticks(x, COND_ORDER); ax.set_ylabel("Score")
    ax.set_title("Response profiles with 95% scene-level bootstrap confidence intervals")
    ax.legend(); ax.grid(True, alpha=.25); fig.tight_layout(); save(fig, "Figure_2")

    # Figure 3
    fig, ax = plt.subplots(figsize=(8.2, 6.2))
    sc = ax.scatter(means["AAS_1_7"], means["CFS_1_7"], c=means["TI_rank_gap"], s=120, edgecolors="black", linewidths=.8)
    for x0, y0, lab in zip(means["AAS_1_7"], means["CFS_1_7"], COND_ORDER):
        ax.annotate(lab, (x0, y0), xytext=(6, 6), textcoords="offset points")
    ax.set_title("Condition means in the AAS–CFS outcome plane")
    ax.set_xlabel("Aesthetic Acceptance Score (AAS)"); ax.set_ylabel("Cognitive Feedback Score (CFS)")
    cbar = fig.colorbar(sc, ax=ax); cbar.set_label("Mean TI (lower is better)")
    ax.grid(True, alpha=.25); fig.tight_layout(); save(fig, "Figure_3")

    # Figure 4
    y = desc["Dual utility mean"].to_numpy()
    err = np.vstack([y-desc["Dual utility CI low"].to_numpy(), desc["Dual utility CI high"].to_numpy()-y])
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    ax.errorbar(COND_ORDER, y, yerr=err, fmt="o", capsize=3)
    ax.set_title("Balanced utility with 95% scene-level bootstrap confidence intervals")
    ax.set_ylabel("Dual utility"); ax.set_xlabel("Condition"); ax.set_ylim(2.8, 4.5); ax.grid(True, alpha=.25)
    fig.tight_layout(); save(fig, "Figure_4")
    print("Figures 1-4 created in outputs/figures.")

if __name__ == "__main__":
    main()
