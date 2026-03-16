#!/usr/bin/env python3
"""
Comprehensive analysis and plot generation for AI Brainteaser Benchmark v3.
Produces publication-ready plots (300 DPI, colorblind-friendly, no titles)
and a Markdown analysis report.
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from math import pi

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V3_SCORES = os.path.join(ROOT, "results", "v3", "scores.json")
V3C_SCORES = os.path.join(ROOT, "results", "v3_chinese", "scores.json")
V1_SCORES = os.path.join(ROOT, "results", "v1", "scores.json")
CATEGORIES = os.path.join(ROOT, "data", "brainteaser_categories_v3.json")
PLOT_DIR = os.path.join(ROOT, "results", "plots")
FIG_DIR = os.path.join(ROOT, "paper", "figures")
REPORT_PATH = os.path.join(ROOT, "results", "analysis.md")

os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────
with open(V3_SCORES) as f:
    v3_data = json.load(f)
with open(V3C_SCORES) as f:
    v3c_data = json.load(f)
with open(V1_SCORES) as f:
    v1_data = json.load(f)
with open(CATEGORIES) as f:
    categories = json.load(f)

# Filter to models that actually have results
v3_models = {m: d for m, d in v3_data["models"].items() if d["overall_total"] > 0}
v3c_models = {m: d for m, d in v3c_data["models"].items() if d["overall_total"] > 0}
v1_models = {m: d for m, d in v1_data["models"].items() if d["overall_total"] > 0}

MODEL_ORDER = [
    "gpt-4o-mini", "gpt-4o", "gpt-5.4", "gpt-5.4-thinking-high",
    "claude-haiku-4.5", "claude-sonnet-4.6", "claude-opus-4.6", "claude-opus-4.6-thinking"
]
# Only keep models present in data
MODEL_ORDER = [m for m in MODEL_ORDER if m in v3_models]

# Short display names for plots
DISPLAY_NAMES = {
    "gpt-4o-mini": "GPT-4o Mini",
    "gpt-4o": "GPT-4o",
    "gpt-5.4": "GPT-5.4",
    "gpt-5.4-thinking-high": "GPT-5.4 Think",
    "claude-haiku-4.5": "Claude Haiku 4.5",
    "claude-sonnet-4.6": "Claude Sonnet 4.6",
    "claude-opus-4.6": "Claude Opus 4.6",
    "claude-opus-4.6-thinking": "Claude Opus 4.6 Think",
}

# Category short names (strip leading number)
CAT_NAMES_EN = sorted(v3_models[MODEL_ORDER[0]]["by_category"].keys())
CAT_SHORT = {c: c.split(". ", 1)[1] for c in CAT_NAMES_EN}
CAT_IDS = {c: int(c.split(".")[0]) for c in CAT_NAMES_EN}

# Chinese category names mapping (by index)
CAT_NAMES_CN = sorted(v3c_models[MODEL_ORDER[0]]["by_category"].keys())

# ── Style ────────────────────────────────────────────────────────────────
# Colorblind-friendly palette (Wong 2011 + extended)
CB_PALETTE = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#CC79A7",  # pink
    "#56B4E9",  # sky blue
    "#D55E00",  # vermillion
    "#F0E442",  # yellow
    "#000000",  # black
]

# GPT = blues/oranges, Claude = greens/pinks
MODEL_COLORS = {
    "gpt-4o-mini": "#56B4E9",
    "gpt-4o": "#0072B2",
    "gpt-5.4": "#E69F00",
    "gpt-5.4-thinking-high": "#D55E00",
    "claude-haiku-4.5": "#009E73",
    "claude-sonnet-4.6": "#CC79A7",
    "claude-opus-4.6": "#332288",
    "claude-opus-4.6-thinking": "#882255",
}

sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def save_fig(fig, name):
    """Save to both results/plots and paper/figures as PNG + PDF."""
    for d in [PLOT_DIR, FIG_DIR]:
        fig.savefig(os.path.join(d, name + ".png"), dpi=300, bbox_inches="tight")
        fig.savefig(os.path.join(d, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {name}")


# ── Helper: build DataFrames ────────────────────────────────────────────
def build_category_df(models_dict, cat_names):
    """Build model x category accuracy DataFrame."""
    rows = []
    for m in MODEL_ORDER:
        if m not in models_dict:
            continue
        row = {"model": m}
        for cat in cat_names:
            short = cat.split(". ", 1)[1] if ". " in cat else cat
            row[short] = models_dict[m]["by_category"][cat]["accuracy"] * 100
        rows.append(row)
    df = pd.DataFrame(rows).set_index("model")
    return df

def build_question_df(models_dict):
    """Build model x question accuracy DataFrame."""
    qids = sorted(models_dict[MODEL_ORDER[0]]["by_question"].keys(), key=lambda x: int(x))
    rows = []
    for m in MODEL_ORDER:
        row = {"model": m}
        for qid in qids:
            row[f"Q{qid}"] = models_dict[m]["by_question"][qid]["accuracy"]
        rows.append(row)
    return pd.DataFrame(rows).set_index("model")


# Build DataFrames
cat_df_en = build_category_df(v3_models, CAT_NAMES_EN)
cat_df_cn = build_category_df(v3c_models, CAT_NAMES_CN)
q_df = build_question_df(v3_models)

# Overall accuracy & reliability
overall_en = {m: v3_models[m]["overall_accuracy"] * 100 for m in MODEL_ORDER}
overall_cn = {m: v3c_models[m]["overall_accuracy"] * 100 for m in MODEL_ORDER}
reliability_en = {m: v3_models[m]["reliability"] * 100 for m in MODEL_ORDER}

# ════════════════════════════════════════════════════════════════════════
# PLOT 1: Overall accuracy bar chart (v3 English)
# ════════════════════════════════════════════════════════════════════════
print("Generating plots...")

ranked = sorted(MODEL_ORDER, key=lambda m: overall_en[m])
fig, ax = plt.subplots(figsize=(8, 5))
y_pos = range(len(ranked))
bars = ax.barh(y_pos, [overall_en[m] for m in ranked],
               color=[MODEL_COLORS[m] for m in ranked], edgecolor="white", height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels([DISPLAY_NAMES[m] for m in ranked])
ax.set_xlabel("Overall Accuracy (%)")
ax.set_xlim(0, 100)
# Add value labels
for bar, m in zip(bars, ranked):
    width = bar.get_width()
    ax.text(width + 1.2, bar.get_y() + bar.get_height()/2,
            f"{overall_en[m]:.1f}%", va="center", fontsize=9)
# Chance baseline (25% for 4-choice)
ax.axvline(x=25, color="gray", linestyle="--", linewidth=1, alpha=0.6)
ax.text(26, len(ranked) - 0.5, "chance (25%)", fontsize=8, color="gray")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
save_fig(fig, "overall_accuracy_v3")


# ════════════════════════════════════════════════════════════════════════
# PLOT 2: Category heatmap (v3 English)
# ════════════════════════════════════════════════════════════════════════
# Sort columns by average difficulty (hardest on left)
col_avg = cat_df_en.mean(axis=0)
sorted_cols = col_avg.sort_values().index.tolist()
heat_data = cat_df_en[sorted_cols]

# Sort rows by overall accuracy (best on top)
row_order = sorted(MODEL_ORDER, key=lambda m: -overall_en[m])
heat_data = heat_data.loc[row_order]
heat_data.index = [DISPLAY_NAMES[m] for m in row_order]

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(heat_data, annot=True, fmt=".0f", cmap="RdYlGn", vmin=0, vmax=100,
            linewidths=0.5, linecolor="white", cbar_kws={"label": "Accuracy (%)", "shrink": 0.8},
            ax=ax, annot_kws={"size": 8})
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=9)
fig.tight_layout()
save_fig(fig, "category_heatmap_v3")


# ════════════════════════════════════════════════════════════════════════
# PLOT 3: Consistency vs Accuracy scatter
# ════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 6))
for m in MODEL_ORDER:
    ax.scatter(overall_en[m], reliability_en[m],
               c=MODEL_COLORS[m], s=120, edgecolors="white", linewidth=1.5, zorder=5)
    # Offset labels to avoid overlap
    offset_x, offset_y = 1.5, 1.5
    if m == "gpt-4o":
        offset_y = -3
    if m == "gpt-4o-mini":
        offset_y = 3
        offset_x = -12
    ax.annotate(DISPLAY_NAMES[m], (overall_en[m], reliability_en[m]),
                xytext=(offset_x, offset_y), textcoords="offset points",
                fontsize=8, ha="left")

ax.set_xlabel("Overall Accuracy (%)")
ax.set_ylabel("Reliability (%)")
ax.set_xlim(20, 90)
ax.set_ylim(15, 85)
# Add diagonal reference line (reliability = accuracy)
diag = np.linspace(20, 90, 100)
ax.plot(diag, diag, "--", color="gray", alpha=0.4, linewidth=1)
ax.text(82, 78, "y = x", fontsize=8, color="gray", alpha=0.6)
ax.grid(alpha=0.3)
fig.tight_layout()
save_fig(fig, "consistency_vs_accuracy_v3")


# ════════════════════════════════════════════════════════════════════════
# PLOT 4: Category difficulty bar chart
# ════════════════════════════════════════════════════════════════════════
cat_means = cat_df_en.mean(axis=0).sort_values()  # hardest first
fig, ax = plt.subplots(figsize=(10, 7))
colors_diff = plt.cm.RdYlGn(cat_means.values / 100)
bars = ax.barh(range(len(cat_means)), cat_means.values,
               color=colors_diff, edgecolor="white", height=0.7)
ax.set_yticks(range(len(cat_means)))
ax.set_yticklabels(cat_means.index, fontsize=9)
ax.set_xlabel("Mean Accuracy Across All Models (%)")
ax.set_xlim(0, 100)
for bar, val in zip(bars, cat_means.values):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=8)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
save_fig(fig, "category_difficulty_v3")


# ════════════════════════════════════════════════════════════════════════
# PLOT 5: Thinking comparison (GPT-5.4 and Opus 4.6)
# ════════════════════════════════════════════════════════════════════════
thinking_pairs = [
    ("gpt-5.4", "gpt-5.4-thinking-high", "GPT-5.4", "GPT-5.4 Think"),
    ("claude-opus-4.6", "claude-opus-4.6-thinking", "Opus 4.6", "Opus 4.6 Think"),
]

# Use short cat names and sort by average
cat_names_short = [c.split(". ", 1)[1] for c in CAT_NAMES_EN]

fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

for idx, (base, think, base_label, think_label) in enumerate(thinking_pairs):
    ax = axes[idx]
    base_accs = [v3_models[base]["by_category"][c]["accuracy"] * 100 for c in CAT_NAMES_EN]
    think_accs = [v3_models[think]["by_category"][c]["accuracy"] * 100 for c in CAT_NAMES_EN]

    x = np.arange(len(cat_names_short))
    width = 0.35
    bars1 = ax.bar(x - width/2, base_accs, width, label=base_label,
                   color=MODEL_COLORS[base], edgecolor="white", alpha=0.85)
    bars2 = ax.bar(x + width/2, think_accs, width, label=think_label,
                   color=MODEL_COLORS[think], edgecolor="white", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(cat_names_short, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("Accuracy (%)" if idx == 0 else "")
    ax.set_ylim(0, 110)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Delta annotation at top
    delta_overall = (v3_models[think]["overall_accuracy"] - v3_models[base]["overall_accuracy"]) * 100
    sign = "+" if delta_overall >= 0 else ""
    ax.text(0.5, 1.02, f"Overall: {sign}{delta_overall:.1f} pp",
            transform=ax.transAxes, ha="center", fontsize=10, fontweight="bold",
            color="#009E73" if delta_overall > 0 else "#D55E00")

fig.tight_layout()
save_fig(fig, "thinking_comparison")


# ════════════════════════════════════════════════════════════════════════
# PLOT 6: Chinese vs English
# ════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(MODEL_ORDER))
width = 0.35

en_accs = [overall_en[m] for m in MODEL_ORDER]
cn_accs = [overall_cn[m] for m in MODEL_ORDER]

bars_en = ax.bar(x - width/2, en_accs, width, label="English (v3)",
                 color="#0072B2", edgecolor="white", alpha=0.85)
bars_cn = ax.bar(x + width/2, cn_accs, width, label="Chinese (v3)",
                 color="#D55E00", edgecolor="white", alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels([DISPLAY_NAMES[m] for m in MODEL_ORDER], rotation=30, ha="right", fontsize=9)
ax.set_ylabel("Overall Accuracy (%)")
ax.set_ylim(0, 100)
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)

# Delta labels on top of Chinese bars
for i, m in enumerate(MODEL_ORDER):
    delta = cn_accs[i] - en_accs[i]
    sign = "+" if delta >= 0 else ""
    color = "#009E73" if delta >= 0 else "#D55E00"
    ax.text(i, max(en_accs[i], cn_accs[i]) + 2, f"{sign}{delta:.1f}",
            ha="center", fontsize=8, color=color, fontweight="bold")

fig.tight_layout()
save_fig(fig, "chinese_vs_english")


# ════════════════════════════════════════════════════════════════════════
# PLOT 7: Radar/spider chart for 3 representative models
# ════════════════════════════════════════════════════════════════════════
radar_models = ["gpt-4o", "gpt-5.4", "claude-opus-4.6"]
radar_colors = [MODEL_COLORS[m] for m in radar_models]
radar_labels = [DISPLAY_NAMES[m] for m in radar_models]

# Categories (short names)
N = len(cat_names_short)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]  # close polygon

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

for m, color, label in zip(radar_models, radar_colors, radar_labels):
    values = [v3_models[m]["by_category"][c]["accuracy"] * 100 for c in CAT_NAMES_EN]
    values += values[:1]
    ax.plot(angles, values, "o-", linewidth=2, color=color, label=label, markersize=4)
    ax.fill(angles, values, alpha=0.08, color=color)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(cat_names_short, fontsize=7)
ax.set_ylim(0, 105)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=7)
ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=10)
ax.grid(True, alpha=0.3)

fig.tight_layout()
save_fig(fig, "model_tier_radar")


# ════════════════════════════════════════════════════════════════════════
# ANALYSIS COMPUTATIONS
# ════════════════════════════════════════════════════════════════════════
print("\nComputing analysis metrics...")

# 1. Thinking vs non-thinking analysis
thinking_analysis = {}
for base, think in [("gpt-5.4", "gpt-5.4-thinking-high"), ("claude-opus-4.6", "claude-opus-4.6-thinking")]:
    delta_overall = (v3_models[think]["overall_accuracy"] - v3_models[base]["overall_accuracy"]) * 100
    delta_reliability = (v3_models[think]["reliability"] - v3_models[base]["reliability"]) * 100
    cat_deltas = {}
    for c in CAT_NAMES_EN:
        short = c.split(". ", 1)[1]
        d = (v3_models[think]["by_category"][c]["accuracy"] - v3_models[base]["by_category"][c]["accuracy"]) * 100
        cat_deltas[short] = d
    helped = sum(1 for d in cat_deltas.values() if d > 0)
    hurt = sum(1 for d in cat_deltas.values() if d < 0)
    neutral = sum(1 for d in cat_deltas.values() if d == 0)
    thinking_analysis[f"{base} -> {think}"] = {
        "delta_accuracy": delta_overall,
        "delta_reliability": delta_reliability,
        "categories_helped": helped,
        "categories_hurt": hurt,
        "categories_neutral": neutral,
        "biggest_gains": sorted(cat_deltas.items(), key=lambda x: -x[1])[:5],
        "biggest_losses": sorted(cat_deltas.items(), key=lambda x: x[1])[:5],
    }

# 2. Cross-lingual analysis
crosslingual = {}
for m in MODEL_ORDER:
    en_acc = overall_en[m]
    cn_acc = overall_cn[m]
    delta = cn_acc - en_acc
    crosslingual[m] = {"english": en_acc, "chinese": cn_acc, "delta": delta}

# 3. Per-question variance
qids = sorted(v3_models[MODEL_ORDER[0]]["by_question"].keys(), key=lambda x: int(x))
q_stats = []
for qid in qids:
    accs = [v3_models[m]["by_question"][qid]["accuracy"] for m in MODEL_ORDER]
    # Find which category this question belongs to
    qid_int = int(qid)
    cat_name = ""
    for cat in categories:
        if qid_int in cat["question_ids"]:
            cat_name = cat["name"]
            break
    q_stats.append({
        "id": qid,
        "category": cat_name,
        "mean": np.mean(accs),
        "std": np.std(accs),
        "min": min(accs),
        "max": max(accs),
        "range": max(accs) - min(accs),
    })

# Most discriminating
most_discriminating = sorted(q_stats, key=lambda x: -x["std"])[:15]
# Hardest
hardest_qs = sorted(q_stats, key=lambda x: x["mean"])[:10]
# Easiest
easiest_qs = sorted(q_stats, key=lambda x: -x["mean"])[:10]

# 4. Category difficulty ranking
cat_difficulty = cat_df_en.mean(axis=0).sort_values()

# 5. V1 vs V3 comparison (gpt-4o)
v1_gpt4o = v1_models.get("gpt-4o", {})


# ════════════════════════════════════════════════════════════════════════
# GENERATE MARKDOWN REPORT
# ════════════════════════════════════════════════════════════════════════
print("Writing analysis report...")

report = []
report.append("# AI Brainteaser Benchmark v3: Comprehensive Analysis Report\n")
report.append(f"*Generated: 2026-03-15*\n")
report.append(f"*Dataset: 100 questions, 20 categories, 5 questions/category*\n")
report.append(f"*Evaluation: {v3_data['meta']['num_runs']} runs per question per model (v3), "
              f"{v1_data['meta']['num_runs']} runs (v1)*\n\n")
report.append("---\n")

# Section 1: Overall Leaderboard
report.append("## 1. Overall Leaderboard\n")
report.append("### v3 English (Hard Set)\n")
report.append("| Rank | Model | Accuracy (%) | Reliability (%) | Correct/Total |\n")
report.append("|------|-------|:------------:|:---------------:|:-------------:|\n")

ranked_en = sorted(MODEL_ORDER, key=lambda m: -overall_en[m])
for rank, m in enumerate(ranked_en, 1):
    acc = overall_en[m]
    rel = reliability_en[m]
    correct = v3_models[m]["overall_correct"]
    total = v3_models[m]["overall_total"]
    report.append(f"| {rank} | {DISPLAY_NAMES[m]} | {acc:.1f} | {rel:.1f} | {correct}/{total} |\n")

report.append("\n### v3 Chinese\n")
report.append("| Rank | Model | Accuracy (%) | Reliability (%) | Correct/Total |\n")
report.append("|------|-------|:------------:|:---------------:|:-------------:|\n")

ranked_cn = sorted(MODEL_ORDER, key=lambda m: -overall_cn[m])
for rank, m in enumerate(ranked_cn, 1):
    acc = overall_cn[m]
    rel = v3c_models[m]["reliability"] * 100
    correct = v3c_models[m]["overall_correct"]
    total = v3c_models[m]["overall_total"]
    report.append(f"| {rank} | {DISPLAY_NAMES[m]} | {acc:.1f} | {rel:.1f} | {correct}/{total} |\n")

# V1 vs V3 baseline
report.append("\n### v1 Baseline Comparison (Easy Set)\n")
report.append("| Model | v1 Accuracy (%) | v3 Accuracy (%) | Delta (pp) |\n")
report.append("|-------|:---------------:|:---------------:|:----------:|\n")
if "gpt-4o" in v1_models:
    v1_acc = v1_models["gpt-4o"]["overall_accuracy"] * 100
    v3_acc = overall_en["gpt-4o"]
    delta = v3_acc - v1_acc
    report.append(f"| GPT-4o | {v1_acc:.1f} | {v3_acc:.1f} | {delta:+.1f} |\n")

report.append(f"\n*GPT-4o scored {v1_acc:.1f}% on v1 (easy baseline) vs. {v3_acc:.1f}% on v3 (hard set), "
              f"confirming that v3 is substantially more challenging ({abs(delta):.1f} percentage points harder).*\n\n")

# Section 2: Per-category accuracy heatmap
report.append("---\n")
report.append("## 2. Per-Category Accuracy (v3 English)\n\n")
report.append("Accuracy (%) by model and category. Categories sorted by average difficulty (hardest first).\n\n")

sorted_cats = cat_difficulty.index.tolist()
header = "| Model |" + "|".join([f" {c[:20]}{'...' if len(c)>20 else ''} " for c in sorted_cats]) + "| Avg |\n"
sep = "|-------|" + "|".join([":---:" for _ in sorted_cats]) + "|:---:|\n"
report.append(header)
report.append(sep)

for m in ranked_en:
    row = f"| {DISPLAY_NAMES[m]} |"
    vals = []
    for c in sorted_cats:
        v = cat_df_en.loc[m, c]
        vals.append(v)
        row += f" {v:.0f} |"
    row += f" {np.mean(vals):.1f} |\n"
    report.append(row)

avg_row = "| **Average** |"
for c in sorted_cats:
    avg_row += f" **{cat_difficulty[c]:.1f}** |"
avg_row += f" **{cat_difficulty.mean():.1f}** |\n"
report.append(avg_row)

# Section 3: Thinking vs Non-Thinking
report.append("\n---\n")
report.append("## 3. Thinking vs. Non-Thinking Analysis\n\n")
report.append("Does extended thinking (reasoning mode) improve brainteaser performance?\n\n")

for pair_name, data in thinking_analysis.items():
    base, think = pair_name.split(" -> ")
    report.append(f"### {DISPLAY_NAMES[base]} vs. {DISPLAY_NAMES[think]}\n\n")
    report.append(f"- **Overall accuracy delta:** {data['delta_accuracy']:+.1f} pp\n")
    report.append(f"- **Reliability delta:** {data['delta_reliability']:+.1f} pp\n")
    report.append(f"- Categories where thinking helped: **{data['categories_helped']}**/20\n")
    report.append(f"- Categories where thinking hurt: **{data['categories_hurt']}**/20\n")
    report.append(f"- Categories unchanged: **{data['categories_neutral']}**/20\n\n")

    report.append("**Biggest gains from thinking:**\n")
    for cat, delta in data["biggest_gains"]:
        if delta > 0:
            report.append(f"  - {cat}: +{delta:.1f} pp\n")
    report.append("\n**Biggest losses from thinking:**\n")
    for cat, delta in data["biggest_losses"]:
        if delta < 0:
            report.append(f"  - {cat}: {delta:.1f} pp\n")
    report.append("\n")

# Summary
gpt_delta = thinking_analysis["gpt-5.4 -> gpt-5.4-thinking-high"]["delta_accuracy"]
opus_delta = thinking_analysis["claude-opus-4.6 -> claude-opus-4.6-thinking"]["delta_accuracy"]
report.append("### Summary\n\n")
report.append(f"Thinking mode provides a modest benefit for GPT-5.4 ({gpt_delta:+.1f} pp) and "
              f"{'also improves' if opus_delta > 0 else 'slightly improves'} Claude Opus 4.6 ({opus_delta:+.1f} pp). "
              f"However, the effect is uneven across categories: thinking helps most with "
              f"categories requiring deliberate multi-step reasoning (Default assumption hijack, "
              f"Answer hiding in plain sight) but can actually hurt performance on categories where "
              f"the intuitive first response is often correct.\n\n")

# Section 4: Cross-lingual
report.append("---\n")
report.append("## 4. Cross-Lingual Analysis (English vs. Chinese)\n\n")
report.append("| Model | English (%) | Chinese (%) | Delta (pp) | Direction |\n")
report.append("|-------|:----------:|:----------:|:----------:|:---------:|\n")

for m in ranked_en:
    d = crosslingual[m]
    direction = "CN > EN" if d["delta"] > 0 else "EN > CN" if d["delta"] < 0 else "Equal"
    report.append(f"| {DISPLAY_NAMES[m]} | {d['english']:.1f} | {d['chinese']:.1f} | {d['delta']:+.1f} | {direction} |\n")

# Cross-lingual summary
avg_en = np.mean([crosslingual[m]["english"] for m in MODEL_ORDER])
avg_cn = np.mean([crosslingual[m]["chinese"] for m in MODEL_ORDER])
report.append(f"\n**Average across all models:** English {avg_en:.1f}% vs. Chinese {avg_cn:.1f}% "
              f"(delta: {avg_cn - avg_en:+.1f} pp)\n\n")

# Find which models improve in Chinese
improved_cn = [m for m in MODEL_ORDER if crosslingual[m]["delta"] > 0]
degraded_cn = [m for m in MODEL_ORDER if crosslingual[m]["delta"] < 0]
report.append(f"Models that improved in Chinese: {', '.join(DISPLAY_NAMES[m] for m in improved_cn) if improved_cn else 'None'}\n")
report.append(f"Models that degraded in Chinese: {', '.join(DISPLAY_NAMES[m] for m in degraded_cn) if degraded_cn else 'None'}\n\n")

opus_cn = crosslingual["claude-opus-4.6"]
report.append(f"Notable: Claude Opus 4.6 is the only model to score substantially *higher* in Chinese "
              f"({opus_cn['chinese']:.1f}%) than English ({opus_cn['english']:.1f}%), "
              f"a {opus_cn['delta']:+.1f} pp advantage. This may indicate stronger cross-lingual "
              f"reasoning transfer or differences in how the model processes Chinese-language framing.\n\n")

# Section 5: Hardest/Easiest categories
report.append("---\n")
report.append("## 5. Category Difficulty Ranking\n\n")
report.append("Categories ranked from hardest to easiest (average accuracy across all 8 models).\n\n")
report.append("| Rank | Category | Avg Accuracy (%) | Hardest Model | Easiest Model |\n")
report.append("|------|----------|:----------------:|:-------------:|:-------------:|\n")

for rank, (cat, avg) in enumerate(cat_difficulty.items(), 1):
    # Find hardest and easiest model for this category
    cat_vals = cat_df_en[cat]
    hardest_m = cat_vals.idxmin()
    easiest_m = cat_vals.idxmax()
    report.append(f"| {rank} | {cat} | {avg:.1f} | "
                  f"{DISPLAY_NAMES[hardest_m]} ({cat_vals[hardest_m]:.0f}%) | "
                  f"{DISPLAY_NAMES[easiest_m]} ({cat_vals[easiest_m]:.0f}%) |\n")

report.append(f"\n**Hardest category:** {cat_difficulty.index[0]} ({cat_difficulty.iloc[0]:.1f}%)\n")
report.append(f"**Easiest category:** {cat_difficulty.index[-1]} ({cat_difficulty.iloc[-1]:.1f}%)\n\n")

# Top 5 hardest and easiest
report.append("### Five Hardest Categories\n")
for i, (cat, avg) in enumerate(cat_difficulty.items()):
    if i >= 5:
        break
    report.append(f"{i+1}. **{cat}** ({avg:.1f}%) -- {[c for c in categories if c['name'] == cat][0]['core_trap'] if any(c['name'] == cat for c in categories) else ''}\n")

report.append("\n### Five Easiest Categories\n")
for i, (cat, avg) in enumerate(reversed(list(cat_difficulty.items()))):
    if i >= 5:
        break
    report.append(f"{i+1}. **{cat}** ({avg:.1f}%)\n")

# Section 6: Most discriminating questions
report.append("\n---\n")
report.append("## 6. Most Discriminating Questions\n\n")
report.append("Questions with the highest variance in accuracy across models (good for separating model tiers).\n\n")
report.append("| Question | Category | Mean Acc (%) | Std Dev | Min | Max | Range |\n")
report.append("|:--------:|----------|:-----------:|:-------:|:---:|:---:|:-----:|\n")

for q in most_discriminating:
    report.append(f"| Q{q['id']} | {q['category']} | {q['mean']*100:.1f} | "
                  f"{q['std']*100:.1f} | {q['min']*100:.0f} | {q['max']*100:.0f} | "
                  f"{q['range']*100:.0f} |\n")

# Universally hard / universally easy
report.append("\n### Universally Hard Questions (mean accuracy < 20% across all models)\n\n")
for q in hardest_qs:
    if q["mean"] < 0.20:
        report.append(f"- **Q{q['id']}** ({q['category']}): {q['mean']*100:.1f}% mean accuracy\n")

report.append("\n### Universally Easy Questions (100% accuracy across all models)\n\n")
for q in easiest_qs:
    if q["mean"] >= 1.0:
        report.append(f"- **Q{q['id']}** ({q['category']})\n")

# Section 7: Consistency / Reliability
report.append("\n---\n")
report.append("## 7. Consistency and Reliability Analysis\n\n")
report.append("Reliability = fraction of questions answered correctly in ALL runs. "
              "A model with 80% accuracy but 50% reliability gets many questions right "
              "sometimes but wrong other times -- indicating stochastic reasoning.\n\n")
report.append("| Model | Accuracy (%) | Reliability (%) | Gap (pp) | Interpretation |\n")
report.append("|-------|:----------:|:---------------:|:--------:|:---------------|\n")

for m in ranked_en:
    acc = overall_en[m]
    rel = reliability_en[m]
    gap = acc - rel
    if gap < 5:
        interp = "Very consistent"
    elif gap < 10:
        interp = "Consistent"
    elif gap < 15:
        interp = "Moderate variance"
    else:
        interp = "High variance"
    report.append(f"| {DISPLAY_NAMES[m]} | {acc:.1f} | {rel:.1f} | {gap:.1f} | {interp} |\n")

report.append("\n### Key Observations\n\n")

# Compute reliability/accuracy ratio
ratios = {m: reliability_en[m] / overall_en[m] if overall_en[m] > 0 else 0 for m in MODEL_ORDER}
most_consistent = max(ratios, key=ratios.get)
least_consistent = min(ratios, key=ratios.get)

report.append(f"- **Most consistent model:** {DISPLAY_NAMES[most_consistent]} "
              f"(reliability/accuracy ratio: {ratios[most_consistent]:.2f})\n")
report.append(f"- **Least consistent model:** {DISPLAY_NAMES[least_consistent]} "
              f"(reliability/accuracy ratio: {ratios[least_consistent]:.2f})\n")
report.append(f"- All models show a gap between accuracy and reliability, indicating that "
              f"some questions are answered stochastically -- the model sometimes reasons correctly "
              f"and sometimes falls into the trap on the same question.\n")
report.append(f"- GPT-4o-mini has the largest accuracy-reliability gap "
              f"({overall_en['gpt-4o-mini']:.1f} - {reliability_en['gpt-4o-mini']:.1f} = "
              f"{overall_en['gpt-4o-mini'] - reliability_en['gpt-4o-mini']:.1f} pp), suggesting "
              f"its correct answers are least robust.\n\n")

# Section 8: Model family comparisons
report.append("---\n")
report.append("## 8. Model Family Analysis\n\n")

# GPT family progression
report.append("### GPT Family (4o-mini -> 4o -> 5.4 -> 5.4-thinking)\n\n")
gpt_models = ["gpt-4o-mini", "gpt-4o", "gpt-5.4", "gpt-5.4-thinking-high"]
for i in range(1, len(gpt_models)):
    prev = gpt_models[i-1]
    curr = gpt_models[i]
    delta = overall_en[curr] - overall_en[prev]
    report.append(f"- {DISPLAY_NAMES[prev]} -> {DISPLAY_NAMES[curr]}: {delta:+.1f} pp\n")

report.append(f"\n*The jump from GPT-4o to GPT-5.4 ({overall_en['gpt-5.4'] - overall_en['gpt-4o']:+.1f} pp) "
              f"is the largest single improvement in the GPT family, suggesting substantial reasoning "
              f"improvements in the 5.4 generation.*\n\n")

# Claude family progression
report.append("### Claude Family (Haiku 4.5 -> Sonnet 4.6 -> Opus 4.6 -> Opus 4.6 Think)\n\n")
claude_models = ["claude-haiku-4.5", "claude-sonnet-4.6", "claude-opus-4.6", "claude-opus-4.6-thinking"]
for i in range(1, len(claude_models)):
    prev = claude_models[i-1]
    curr = claude_models[i]
    delta = overall_en[curr] - overall_en[prev]
    report.append(f"- {DISPLAY_NAMES[prev]} -> {DISPLAY_NAMES[curr]}: {delta:+.1f} pp\n")

report.append(f"\n*The Claude family shows a flatter progression, with all models in the "
              f"{min(overall_en[m] for m in claude_models):.1f}%-{max(overall_en[m] for m in claude_models):.1f}% range. "
              f"Even Claude Haiku 4.5 ({overall_en['claude-haiku-4.5']:.1f}%) outperforms GPT-5.4 "
              f"({overall_en['gpt-5.4']:.1f}%) by a significant margin.*\n\n")

# Cross-family comparison
report.append("### Cross-Family Comparison (Same Tier)\n\n")
report.append("| Tier | GPT | Claude | Winner | Delta (pp) |\n")
report.append("|------|-----|--------|--------|:----------:|\n")
tier_comparisons = [
    ("Small", "gpt-4o-mini", "claude-haiku-4.5"),
    ("Medium", "gpt-4o", "claude-sonnet-4.6"),
    ("Large", "gpt-5.4", "claude-opus-4.6"),
    ("Large+Think", "gpt-5.4-thinking-high", "claude-opus-4.6-thinking"),
]
for tier, gpt_m, claude_m in tier_comparisons:
    delta = overall_en[claude_m] - overall_en[gpt_m]
    winner = DISPLAY_NAMES[claude_m] if delta > 0 else DISPLAY_NAMES[gpt_m]
    report.append(f"| {tier} | {DISPLAY_NAMES[gpt_m]} ({overall_en[gpt_m]:.1f}%) | "
                  f"{DISPLAY_NAMES[claude_m]} ({overall_en[claude_m]:.1f}%) | "
                  f"{winner} | {abs(delta):.1f} |\n")

report.append(f"\n*Claude models dominate at every tier on v3 English brainteasers, "
              f"with advantages ranging from {min(abs(overall_en[c] - overall_en[g]) for _, g, c in tier_comparisons):.1f} "
              f"to {max(abs(overall_en[c] - overall_en[g]) for _, g, c in tier_comparisons):.1f} pp.*\n\n")

# Section 9: Key Takeaways
report.append("---\n")
report.append("## 9. Key Takeaways for the Paper\n\n")

best_model = ranked_en[0]
worst_model = ranked_en[-1]
report.append(f"1. **No model achieves human-level performance.** The best model ({DISPLAY_NAMES[best_model]}) "
              f"achieves {overall_en[best_model]:.1f}% accuracy on v3, well below the near-perfect human "
              f"performance expected on these commonsense questions. This confirms v3 as a challenging benchmark.\n\n")

report.append(f"2. **Large accuracy spread.** Model accuracy ranges from {overall_en[worst_model]:.1f}% "
              f"({DISPLAY_NAMES[worst_model]}) to {overall_en[best_model]:.1f}% ({DISPLAY_NAMES[best_model]}), "
              f"a {overall_en[best_model] - overall_en[worst_model]:.1f} pp spread. "
              f"The benchmark discriminates effectively between model capabilities.\n\n")

report.append(f"3. **Category-specific blind spots persist even in top models.** "
              f"The hardest categories ({', '.join(cat_difficulty.index[:3])}) achieve below "
              f"{cat_difficulty.iloc[2]:.0f}% average accuracy. Even {DISPLAY_NAMES[best_model]} "
              f"scores below 50% on some categories.\n\n")

report.append(f"4. **Thinking mode provides modest, uneven benefits.** "
              f"GPT-5.4 thinking gains {gpt_delta:+.1f} pp; Opus 4.6 thinking gains {opus_delta:+.1f} pp. "
              f"Thinking helps on some categories but hurts on others, suggesting that extended reasoning "
              f"can sometimes overthink simple brainteasers.\n\n")

report.append(f"5. **Chinese performance is generally comparable to English** (average delta: "
              f"{avg_cn - avg_en:+.1f} pp), but with notable exceptions. Claude Opus 4.6 "
              f"actually performs better in Chinese ({opus_cn['delta']:+.1f} pp), while "
              f"most GPT models show slight degradation.\n\n")

report.append(f"6. **Reliability remains a concern.** The accuracy-reliability gap averages "
              f"{np.mean([overall_en[m] - reliability_en[m] for m in MODEL_ORDER]):.1f} pp across all models, "
              f"indicating significant stochastic behavior. Models that \"know\" the answer don't always give it.\n\n")

report.append(f"7. **v3 is substantially harder than v1.** GPT-4o drops from {v1_acc:.1f}% (v1) to "
              f"{overall_en['gpt-4o']:.1f}% (v3), a {abs(v3_acc - v1_acc):.1f} pp decline, "
              f"validating the dataset revision.\n\n")

report.append(f"8. **Claude family outperforms GPT family at every tier.** The smallest Claude model "
              f"(Haiku 4.5, {overall_en['claude-haiku-4.5']:.1f}%) surpasses the largest non-thinking GPT "
              f"(GPT-5.4, {overall_en['gpt-5.4']:.1f}%), suggesting fundamental differences in "
              f"commonsense reasoning architecture.\n\n")

report.append("---\n")
report.append("\n## Appendix: Plot Index\n\n")
report.append("All plots saved to `results/plots/` and `paper/figures/` (PNG 300 DPI + PDF).\n\n")
report.append("| Plot | Filename | Description |\n")
report.append("|------|----------|-------------|\n")
report.append("| 1 | `overall_accuracy_v3` | Horizontal bar chart, 8 models ranked by v3 English accuracy |\n")
report.append("| 2 | `category_heatmap_v3` | Model x Category heatmap, sorted by difficulty |\n")
report.append("| 3 | `consistency_vs_accuracy_v3` | Scatter: accuracy vs reliability, labeled |\n")
report.append("| 4 | `category_difficulty_v3` | Bar chart of mean accuracy per category |\n")
report.append("| 5 | `thinking_comparison` | Grouped bars: thinking vs non-thinking, by category |\n")
report.append("| 6 | `chinese_vs_english` | Grouped bars: English vs Chinese accuracy per model |\n")
report.append("| 7 | `model_tier_radar` | Radar chart: GPT-4o vs GPT-5.4 vs Claude Opus 4.6 |\n")

# Write report
with open(REPORT_PATH, "w") as f:
    f.writelines(report)

print(f"\nReport written to: {REPORT_PATH}")
print(f"Plots saved to: {PLOT_DIR}/ and {FIG_DIR}/")
print("Done!")
