"""Corpus figures with Warm Research palette. Generates 6 figures for presentation."""
import re
import shutil
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


# Top-level / generic categories to exclude when picking most descriptive from record_appears_in
_GENERIC_CATEGORIES = frozenset({
    "All", "The College", "Social Sciences Division", "Arts & Humanities Division",
    "Physical Sciences Division", "Biological Sciences Division",
    "Centers and Institutes", "Social Sciences", "Physical Sciences", "Humanities",
})


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


def _descriptive_category(thesis: dict) -> str:
    """Most descriptive category from record_appears_in: prefer program/department over division.

    Filters out generic top-level entries (All, The College, * Division) and picks the most
    specific remaining entry for richer analysis.
    """
    appears = thesis.get("record_appears_in") or []
    if isinstance(appears, str):
        appears = [appears]
    if not appears:
        return _primary_category(thesis)
    # Filter out generic; take the most specific (last non-generic, or last before "All")
    specific = [a.strip() for a in appears if a.strip() not in _GENERIC_CATEGORIES]
    if specific:
        return specific[-1]  # Last is often most specific (e.g. "Harris School" after "Public Policy")
    # Fallback: use first non-All
    for a in appears:
        a = a.strip()
        if a and a != "All":
            return a
    return "Uncategorized"


def _text_for_embedding(thesis: dict, use_keywords: bool = False) -> str:
    """Text to embed: abstract (+ title) or keywords joined."""
    if use_keywords and thesis.get("keywords"):
        return " ".join(thesis["keywords"])
    title = thesis.get("title") or ""
    abstract = thesis.get("abstract") or ""
    return f"{title}. {abstract}"[:512].strip() or "empty"


def _text_combined(thesis: dict, max_chars: int = 2000) -> str:
    """Combined title + abstract + keywords for full-thesis embedding or n-gram extraction."""
    parts = [
        thesis.get("title") or "",
        thesis.get("abstract") or "",
        " ".join(str(k) for k in (thesis.get("keywords") or [])),
    ]
    return " ".join(parts)[:max_chars].strip() or "empty"


# Stopwords and uninformative words for 2-grams (not insightful for topical analysis)
_STOPWORDS = frozenset({
    "the", "of", "and", "to", "in", "a", "is", "for", "on", "with", "as", "by",
    "that", "this", "from", "at", "be", "or", "an", "it", "its", "are", "was",
    "were", "been", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "such", "than", "so", "if", "but",
    "et", "al", "only", "no", "also", "just", "even", "however", "therefore",
    "abstract", "paper", "study", "thesis", "examines", "investigates", "findings",
    "suggest", "these", "those", "how", "when", "where", "what", "which", "who",
})


def _extract_bigrams(theses: list[dict]) -> list[tuple[str, str]]:
    """Extract bigrams from combined title+abstract+keywords; filter stopwords and author patterns."""
    all_bigrams: list[tuple[str, str]] = []
    year_re = re.compile(r"^\d{4}$")
    for t in theses:
        text = _text_combined(t).lower()
        tokens = re.findall(r"[a-z]{2,}", text)
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 in _STOPWORDS or w2 in _STOPWORDS:
                continue
            if year_re.match(w2):
                continue
            if len(w1) < 2 or len(w2) < 2:
                continue
            all_bigrams.append((w1, w2))
    return all_bigrams


def _salient_bigrams(theses: list[dict], top_n: int = 25, max_doc_freq_ratio: float = 0.85) -> list[tuple[tuple[str, str], float]]:
    """Return top bigrams by saliency: freq * idf, filtering very common (low-saliency) phrases."""
    all_bigrams = _extract_bigrams(theses)
    counts = Counter(all_bigrams)
    n_docs = len(theses)
    year_re = re.compile(r"^\d{4}$")
    doc_freq: Counter[tuple[str, str]] = Counter()
    for t in theses:
        text = _text_combined(t).lower()
        tokens = re.findall(r"[a-z]{2,}", text)
        seen: set[tuple[str, str]] = set()
        for j in range(len(tokens) - 1):
            w1, w2 = tokens[j], tokens[j + 1]
            if w1 in _STOPWORDS or w2 in _STOPWORDS or year_re.match(w2):
                continue
            if len(w1) < 2 or len(w2) < 2:
                continue
            bg = (w1, w2)
            if bg not in seen:
                seen.add(bg)
                doc_freq[bg] += 1
    scored = []
    for bg, freq in counts.items():
        df = doc_freq.get(bg, 0)
        if df > max_doc_freq_ratio * n_docs:
            continue
        idf = np.log(n_docs / (df + 1)) + 1
        scored.append((bg, freq * idf))
    scored.sort(key=lambda x: -x[1])
    return scored[:top_n]


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


def fig_02_embedding_clusters(theses: list[dict], embed_loader: EmbeddingLoader, out_dir: Path) -> None:
    """t-SNE of combined title+abstract+keywords embeddings, colored by k-means cluster.

    Embedding source: full thesis text (title + abstract + keywords) for richer semantic clusters.
    """
    texts = [_text_combined(t) for t in theses]
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
    ax.set_title("Thesis embedding clusters (title + abstract + keywords)", color=PALETTE["charcoal"])
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=CLUSTER_COLORS[i], label=f"Cluster {i}", markersize=8) for i in range(n_clusters)]
    ax.legend(handles=handles, fontsize=8, frameon=True, facecolor=PALETTE["white"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "02_embedding_clusters.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_03_top_categories(theses: list[dict], out_dir: Path) -> None:
    """Two-panel: (A) top categories; (B) composition of MA Thesis Archive (other categories within)."""
    categories = [_descriptive_category(t) for t in theses]
    counts = Counter(categories)
    top = counts.most_common(15)
    if not top:
        return

    def _appears_str(t: dict) -> str:
        return " ".join(str(x) for x in (t.get("record_appears_in") or [])).lower()

    macss_count = sum(
        1 for t in theses
        if t.get("is_macss")
        or "macss" in _appears_str(t)
        or "computational social sciences" in _appears_str(t)
    )

    # Exclude from Panel B: MA Thesis Archive itself, All, and generic top-level
    exclude_panel_b = _GENERIC_CATEGORIES | {"MA Thesis Archive", "All"}

    ma_thesis_theses = [t for t in theses if _descriptive_category(t) == "MA Thesis Archive"]
    other_cats: Counter[str] = Counter()
    for t in ma_thesis_theses:
        appears = t.get("record_appears_in") or []
        if isinstance(appears, str):
            appears = [appears]
        for a in appears:
            a = a.strip()
            if a and a not in exclude_panel_b:
                other_cats[a] += 1
    panel_b_top = other_cats.most_common(15)
    panel_b_labels = [x[0][:35] for x in panel_b_top]
    panel_b_values = [x[1] for x in panel_b_top]

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A
    labels = [x[0][:40] for x in top]
    values = [x[1] for x in top]
    bars = ax_a.barh(range(len(labels)), values, color=PALETTE["steel"], edgecolor=PALETTE["white"], alpha=0.85)
    ax_a.invert_yaxis()
    for i, (lab, val) in enumerate(zip(labels, values)):
        if "computational" in lab.lower() or "macss" in lab.lower():
            bars[i].set_facecolor(PALETTE["warm_orange"])
    ax_a.set_yticks(range(len(labels)))
    ax_a.set_yticklabels(labels, fontsize=9)
    ax_a.set_xlabel("Number of theses", color=PALETTE["charcoal"])
    ax_a.set_title(f"(A) Top categories. MACSS ≈ {macss_count} theses.", color=PALETTE["charcoal"])
    _figure_style(ax_a)

    # Panel B
    if panel_b_top:
        bars_b = ax_b.barh(range(len(panel_b_labels)), panel_b_values, color=PALETTE["steel"], edgecolor=PALETTE["white"], alpha=0.85)
        ax_b.invert_yaxis()
        for i, lab in enumerate(panel_b_labels):
            if "computational" in lab.lower() or "macss" in lab.lower():
                bars_b[i].set_facecolor(PALETTE["warm_orange"])
        ax_b.set_yticks(range(len(panel_b_labels)))
        ax_b.set_yticklabels(panel_b_labels, fontsize=9)
        ax_b.set_xlabel("Number of theses", color=PALETTE["charcoal"])
        ax_b.set_title(f"(B) MA Thesis Archive: other categories (n={len(ma_thesis_theses)})", color=PALETTE["charcoal"])
    else:
        ax_b.text(0.5, 0.5, "No other categories", ha="center", va="center", transform=ax_b.transAxes)
        ax_b.set_title("(B) MA Thesis Archive composition", color=PALETTE["charcoal"])
    _figure_style(ax_b)

    fig.tight_layout()
    fig.savefig(out_dir / "03_top_categories.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()


def fig_04_top_bigrams(theses: list[dict], out_dir: Path) -> None:
    """Bar chart of most salient 2-grams (freq × IDF), filtered for topical phrases."""
    scored = _salient_bigrams(theses, top_n=25)
    if not scored:
        return
    labels = [f"{a} {b}" for (a, b), _ in scored]
    values = [int(s) for _, s in scored]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(range(len(labels)), values, color=PALETTE["warm_orange"], edgecolor=PALETTE["white"], alpha=0.85)
    ax.invert_yaxis()
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Saliency (freq × IDF)", color=PALETTE["charcoal"])
    ax.set_title("Most salient 2-grams (title + abstract + keywords)", color=PALETTE["charcoal"])
    _figure_style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "04_top_bigrams.png", dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
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
        fig_02_path = out_dir / "02_embedding_clusters.png"
        old_path = out_dir / "02_embedding_clusters_old.png"
        legacy_path = out_dir / "02_embedding_by_keywords.png"
        if fig_02_path.exists():
            shutil.copy2(fig_02_path, old_path)
        elif legacy_path.exists():
            shutil.copy2(legacy_path, old_path)
        fig_02_embedding_clusters(theses, embed_loader, out_dir)
        saved.append(out_dir / "02_embedding_clusters.png")

    fig_03_top_categories(theses, out_dir)
    saved.append(out_dir / "03_top_categories.png")
    fig_04_top_bigrams(theses, out_dir)
    saved.append(out_dir / "04_top_bigrams.png")
    fig_05_theses_by_year(theses, out_dir)
    saved.append(out_dir / "05_theses_by_year.png")
    fig_06_abstract_length(theses, out_dir)
    saved.append(out_dir / "06_abstract_length.png")

    return saved
