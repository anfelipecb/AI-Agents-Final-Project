"""Corpus figures with Warm Research palette. Generates 6 figures for presentation."""
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..config import FIGURES_DIR
from ..data import CorpusLoader
from ..models import EmbeddingLoader

# White figure background; serif font for titles and labels (Times New Roman when available)
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 11

# Warm Research palette
PALETTE = {
    "charcoal": "#2D3142",
    "warm_orange": "#EF8354",
    "steel": "#4F5D75",
    "light_gray": "#BFC0C0",
    "white": "#FFFFFF",
}
FIGURE_BG = PALETTE["white"]
# For overlapping fills
TRANSPARENT_RED = "#E07A5F80"
TRANSPARENT_BLUE = "#3D5A8080"
# Category colors (fig 01) – distinct for Record Appears In
CATEGORY_COLORS = [
    "#1B4965", "#5FA8D3", "#62B6CB", "#BEE9E8", "#CAE9FF",
    "#2D3142", "#EF8354", "#4F5D75", "#3D5A80", "#E07A5F",
    "#6B7B8C", "#8B7355",
]
# Clustering colors (fig 02) – high-contrast for k-means clusters
CLUSTER_COLORS = [
    "#E63946", "#2A9D8F", "#E9C46A", "#264653", "#F4A261", "#9B5DE5",
    "#00BBF9", "#F15BB5", "#00F5D4", "#7B2CBF",
]


def _primary_category(thesis: dict) -> str:
    """Derive primary_category from record_appears_in or return Uncategorized."""
    if thesis.get("primary_category"):
        return thesis["primary_category"]
    appears = thesis.get("record_appears_in") or []
    if isinstance(appears, str):
        appears = [appears]
    if appears:
        first = appears[0]
        return first.split(">")[-1].strip() if ">" in first else first
    return "Uncategorized"


def _text_for_embedding(thesis: dict, use_keywords: bool = False) -> str:
    """Text to embed: abstract (+ title) or keywords joined."""
    if use_keywords and thesis.get("keywords"):
        return " ".join(thesis["keywords"])
    title = thesis.get("title") or ""
    abstract = thesis.get("abstract") or ""
    return f"{title}. {abstract}"[:512].strip() or "empty"


def _figure_style(ax: plt.Axes) -> None:
    """Apply Warm Research style: white background, no top/right spines."""
    ax.set_facecolor(FIGURE_BG)
    ax.figure.patch.set_facecolor(FIGURE_BG)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=PALETTE["charcoal"])


def fig_01_embedding_by_category(theses: list[dict], embed_loader: EmbeddingLoader, out_dir: Path) -> None:
    """t-SNE of abstract embeddings colored by primary_category."""
    texts = [_text_for_embedding(t, use_keywords=False) for t in theses]
    valid = [(i, t) for i, t in enumerate(theses) if texts[i].strip() and texts[i] != "empty"]
    if not valid:
        return
    idx, _ = zip(*valid)
    X = embed_loader.get_embeddings([texts[i] for i in idx])
    from sklearn.manifold import TSNE
    xy = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X) - 1)).fit_transform(X)
    categories = [_primary_category(theses[i]) for i in idx]
    top_cats = Counter(categories).most_common(12)
    cat_to_color = {c: CATEGORY_COLORS[i % len(CATEGORY_COLORS)] for i, c in enumerate([x[0] for x in top_cats])}
    colors = [cat_to_color.get(c, PALETTE["light_gray"]) for c in categories]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xy[:, 0], xy[:, 1], c=colors, s=40, alpha=0.7, edgecolors=PALETTE["white"], linewidths=0.5)
    ax.set_xlabel("t-SNE 1", color=PALETTE["charcoal"])
    ax.set_ylabel("t-SNE 2", color=PALETTE["charcoal"])
    ax.set_title("Thesis abstracts by category (Record Appears in)", color=PALETTE["charcoal"])
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=cat_to_color.get(c, PALETTE["light_gray"]), label=c, markersize=8) for c in [x[0] for x in top_cats]]
    ax.legend(handles=handles, fontsize=8, frameon=True, facecolor=PALETTE["white"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "01_embedding_by_category.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_02_embedding_by_keywords(theses: list[dict], embed_loader: EmbeddingLoader, out_dir: Path) -> None:
    """t-SNE of keyword (or abstract fallback) embeddings, colored by k-means cluster."""
    texts = [_text_for_embedding(t, use_keywords=True) for t in theses]
    valid = [(i, t) for i, t in enumerate(theses) if texts[i].strip() and texts[i] != "empty"]
    if not valid:
        return
    idx, _ = zip(*valid)
    X = embed_loader.get_embeddings([texts[i] for i in idx])
    from sklearn.manifold import TSNE
    from sklearn.cluster import KMeans
    n_clusters = min(6, len(X) - 1) if len(X) > 1 else 1
    if n_clusters < 2:
        return
    xy = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X) - 1)).fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(X)
    labels = kmeans.labels_
    colors = [CLUSTER_COLORS[l % len(CLUSTER_COLORS)] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xy[:, 0], xy[:, 1], c=colors, s=40, alpha=0.7, edgecolors=PALETTE["white"], linewidths=0.5)
    ax.set_xlabel("t-SNE 1", color=PALETTE["charcoal"])
    ax.set_ylabel("t-SNE 2", color=PALETTE["charcoal"])
    ax.set_title("Thesis keyword/abstract embedding clusters", color=PALETTE["charcoal"])
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=CLUSTER_COLORS[i], label=f"Cluster {i}", markersize=8) for i in range(n_clusters)]
    ax.legend(handles=handles, fontsize=8, frameon=True, facecolor=PALETTE["white"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "02_embedding_by_keywords.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_03_top_categories(theses: list[dict], out_dir: Path) -> None:
    """Bar chart of top primary categories; annotate MACSS count."""
    categories = [_primary_category(t) for t in theses]
    counts = Counter(categories)
    top = counts.most_common(15)
    if not top:
        return
    labels = [x[0][:35] for x in top]
    values = [x[1] for x in top]
    macss_count = sum(1 for t in theses if t.get("is_macss") or "macss" in " ".join(t.get("record_appears_in") or []).lower() or "computational social sciences" in " ".join(t.get("record_appears_in") or []).lower())

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(labels)), values, color=PALETTE["steel"], edgecolor=PALETTE["white"], alpha=0.85)
    for i, (lab, val) in enumerate(zip(labels, values)):
        if "computational" in lab.lower() or "macss" in lab.lower():
            bars[i].set_facecolor(PALETTE["warm_orange"])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Number of theses", color=PALETTE["charcoal"])
    ax.set_title(f"Top categories (Record Appears in). MACSS ≈ {macss_count} theses.", color=PALETTE["charcoal"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "03_top_categories.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_04_keyword_clusters(theses: list[dict], out_dir: Path) -> None:
    """Bar chart of most frequent keywords."""
    all_kw = []
    for t in theses:
        kw = t.get("keywords") or []
        if isinstance(kw, str):
            kw = [k.strip() for k in kw.split(",")]
        all_kw.extend(kw)
    counts = Counter(all_kw).most_common(20)
    if not counts:
        return
    labels = [x[0][:30] for x in counts]
    values = [x[1] for x in counts]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(range(len(labels)), values, color=PALETTE["warm_orange"], edgecolor=PALETTE["white"], alpha=0.85)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Frequency", color=PALETTE["charcoal"])
    ax.set_title("Most frequent keywords", color=PALETTE["charcoal"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "04_keyword_clusters.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_05_theses_by_year(theses: list[dict], out_dir: Path) -> None:
    """Bar/line chart of thesis count by year."""
    years = []
    for t in theses:
        y = t.get("year")
        if isinstance(y, int) and 1990 <= y <= 2030:
            years.append(y)
        elif isinstance(y, str):
            try:
                y = int(y)
                if 1990 <= y <= 2030:
                    years.append(y)
            except ValueError:
                pass
    if not years:
        return
    counts = Counter(years)
    sorted_years = sorted(counts.keys())
    values = [counts[y] for y in sorted_years]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(sorted_years, values, color=PALETTE["steel"], edgecolor=PALETTE["white"], alpha=0.85)
    ax.set_xlabel("Year", color=PALETTE["charcoal"])
    ax.set_ylabel("Number of theses", color=PALETTE["charcoal"])
    ax.set_title("Theses by year", color=PALETTE["charcoal"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "05_theses_by_year.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_06_abstract_length(theses: list[dict], out_dir: Path) -> None:
    """Histogram of abstract length (exclude zero)."""
    lengths = [len((t.get("abstract") or "").strip()) for t in theses if (t.get("abstract") or "").strip()]
    if not lengths:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(lengths, bins=min(40, len(set(lengths)) or 1), color=PALETTE["steel"], edgecolor=PALETTE["white"], alpha=0.7)
    ax.set_xlabel("Abstract length (characters)", color=PALETTE["charcoal"])
    ax.set_ylabel("Count", color=PALETTE["charcoal"])
    ax.set_title("Distribution of abstract lengths", color=PALETTE["charcoal"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "06_abstract_length.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def generate_corpus_figures(
    corpus_path: Path | None = None,
    figures_dir: Path | None = None,
    skip_embedding_figures: bool = False,
) -> list[Path]:
    """Load corpus, generate all 6 figures, save to figures_dir. Returns list of saved paths."""
    out_dir = figures_dir or FIGURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    loader = CorpusLoader(path=corpus_path)
    theses = loader.load()
    if not theses:
        return []
    saved = []

    if not skip_embedding_figures:
        embed_loader = EmbeddingLoader()
        fig_01_embedding_by_category(theses, embed_loader, out_dir)
        saved.append(out_dir / "01_embedding_by_category.png")
        fig_02_embedding_by_keywords(theses, embed_loader, out_dir)
        saved.append(out_dir / "02_embedding_by_keywords.png")

    fig_03_top_categories(theses, out_dir)
    saved.append(out_dir / "03_top_categories.png")
    fig_04_keyword_clusters(theses, out_dir)
    saved.append(out_dir / "04_keyword_clusters.png")
    fig_05_theses_by_year(theses, out_dir)
    saved.append(out_dir / "05_theses_by_year.png")
    fig_06_abstract_length(theses, out_dir)
    saved.append(out_dir / "06_abstract_length.png")

    return saved
