#!/usr/bin/env python3
"""Analyze benchmark results and generate plots."""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
DATA_DIR = ROOT_DIR / "data"
PLOT_DIR = RESULTS_DIR / "plots"
FIGURE_DIR = ROOT_DIR / "paper" / "figures"


def load_scores() -> dict:
    with open(RESULTS_DIR / "scores.json") as f:
        return json.load(f)


def load_categories() -> list[dict]:
    with open(DATA_DIR / "brainteaser_categories.json") as f:
        return json.load(f)


def setup_style():
    sns.set_theme(style="whitegrid", font_scale=1.1)
    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
    })


def save_fig(fig: plt.Figure, name: str):
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(PLOT_DIR / f"{name}.png")
    fig.savefig(FIGURE_DIR / f"{name}.pdf")
    plt.close(fig)
    print(f"  Saved {name}")


def plot_overall_accuracy(scores: dict):
    """Bar chart of overall accuracy per model, ranked."""
    models = scores["models"]
    data = sorted(
        [(name, m["overall_accuracy"]) for name, m in models.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    names, accs = zip(*data)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("Set2", len(names))
    bars = ax.barh(range(len(names)), [a * 100 for a in accs], color=colors)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xlabel("Accuracy (%)")
    ax.set_xlim(0, 100)
    ax.invert_yaxis()

    for bar, acc in zip(bars, accs):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{acc * 100:.1f}%", va="center", fontsize=9)

    fig.tight_layout()
    save_fig(fig, "overall_accuracy")


def plot_category_heatmap(scores: dict, categories: list[dict]):
    """Heatmap of model × category accuracy."""
    models = scores["models"]
    cat_names = [c["name"] for c in categories]
    cat_keys = {f"{c['id']}. {c['name']}": c["name"] for c in categories}

    model_names = sorted(models.keys())
    matrix = []

    for model_name in model_names:
        row = []
        by_cat = models[model_name]["by_category"]
        for c in categories:
            key = f"{c['id']}. {c['name']}"
            cat_data = by_cat.get(key, {})
            row.append(cat_data.get("accuracy", 0) * 100)
        matrix.append(row)

    df = pd.DataFrame(matrix, index=model_names, columns=cat_names)

    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(
        df, annot=True, fmt=".0f", cmap="RdYlGn",
        vmin=0, vmax=100, linewidths=0.5, ax=ax,
        cbar_kws={"label": "Accuracy (%)"},
    )
    ax.set_xlabel("Category")
    ax.set_ylabel("Model")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    fig.tight_layout()
    save_fig(fig, "category_heatmap")


def plot_consistency_vs_accuracy(scores: dict):
    """Scatter plot: accuracy vs reliability per model."""
    models = scores["models"]
    data = [
        (name, m["overall_accuracy"] * 100, m["reliability"] * 100)
        for name, m in models.items()
    ]
    names, accs, rels = zip(*data)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = sns.color_palette("Set2", len(names))
    ax.scatter(accs, rels, c=colors, s=100, zorder=5)

    for name, x, y in zip(names, accs, rels):
        ax.annotate(name, (x, y), textcoords="offset points",
                    xytext=(5, 5), fontsize=8)

    ax.set_xlabel("Overall Accuracy (%)")
    ax.set_ylabel("Reliability (% questions ≥80% correct)")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    save_fig(fig, "consistency_vs_accuracy")


def plot_category_difficulty(scores: dict, categories: list[dict]):
    """Bar chart of average accuracy per category across all models."""
    models = scores["models"]
    cat_avg = {}

    for c in categories:
        key = f"{c['id']}. {c['name']}"
        accs = []
        for m in models.values():
            cat_data = m["by_category"].get(key, {})
            if cat_data.get("total", 0) > 0:
                accs.append(cat_data["accuracy"] * 100)
        cat_avg[c["name"]] = np.mean(accs) if accs else 0

    sorted_cats = sorted(cat_avg.items(), key=lambda x: x[1])
    names, avgs = zip(*sorted_cats)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.RdYlGn(np.array(avgs) / 100)
    ax.barh(range(len(names)), avgs, color=colors)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Average Accuracy Across Models (%)")
    ax.set_xlim(0, 100)
    fig.tight_layout()
    save_fig(fig, "category_difficulty")


def print_summary(scores: dict):
    """Print a text summary of results."""
    models = scores["models"]
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 60)

    ranked = sorted(
        [(name, m["overall_accuracy"]) for name, m in models.items()],
        key=lambda x: x[1],
        reverse=True,
    )

    print(f"\n{'Model':<25s} {'Accuracy':>10s} {'Reliability':>12s}")
    print("-" * 50)
    for name, acc in ranked:
        rel = models[name]["reliability"]
        print(f"{name:<25s} {acc*100:>9.1f}% {rel*100:>10.1f}%")

    print("\n" + "=" * 60)


def main():
    setup_style()
    scores = load_scores()
    categories = load_categories()

    print("Generating plots...")
    plot_overall_accuracy(scores)
    plot_category_heatmap(scores, categories)
    plot_consistency_vs_accuracy(scores)
    plot_category_difficulty(scores, categories)
    print_summary(scores)
    print(f"\nPlots saved to {PLOT_DIR} and {FIGURE_DIR}")


if __name__ == "__main__":
    main()
