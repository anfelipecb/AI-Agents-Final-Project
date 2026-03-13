"""MACSS thesis scraper for Knowledge UChicago. Uses httpx and BeautifulSoup."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from ..config import (
    BASE_URL,
    INTERMEDIATE_PATH,
    LOGS_DIR,
    MACSS_PATH,
    MAX_RETRIES,
    REQUEST_DELAY,
    RETRY_BACKOFF,
    SEARCH_URL,
)
from .corpus import extract_year, infer_methodology, save_corpus, setup_logging

logger = setup_logging()


def fetch_with_retry(client: httpx.Client, url: str) -> httpx.Response | None:
    """Fetch URL with retries and exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            r = client.get(url, follow_redirects=True, timeout=30.0)
            r.raise_for_status()
            return r
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF ** attempt)
    return None


def parse_search_page(html: str, base: str) -> list[str]:
    """Extract record URLs from search results page."""
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/record/" in href or "/handle/" in href:
            full = urljoin(base, href)
            if full not in seen and "knowledge.uchicago.edu" in full:
                seen.add(full)
                urls.append(full)
    return urls


def parse_record_page(html: str, url: str, soup: BeautifulSoup | None = None) -> dict | None:
    """Extract thesis metadata from record page HTML."""
    if soup is None:
        soup = BeautifulSoup(html, "html.parser")

    title = ""
    for sel in ["h1", ".title", "[class*='title']", "meta[property='og:title']"]:
        el = soup.select_one(sel)
        if el:
            title = el.get("content", el.get_text(strip=True))
            if title:
                break
    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    abstract = ""
    for sel in [".abstract", ".description", "[class*='abstract']", "[class*='description']"]:
        el = soup.select_one(sel)
        if el:
            abstract = el.get_text(strip=True)
            if len(abstract) > 50:
                break
    if not abstract:
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            abstract = meta["content"]

    author = ""
    for sel in [".author", ".creator", "[class*='author']", "[class*='creator']"]:
        el = soup.select_one(sel)
        if el:
            author = el.get_text(strip=True)
            if author:
                break

    year: int | None = None
    for sel in [".date", "[class*='year']", "time"]:
        for el in soup.select(sel):
            y = extract_year(el.get_text())
            if y:
                year = y
                break
        if year:
            break
    if not year:
        year = extract_year(html) or extract_year(soup.get_text())

    record_id = url.rstrip("/").split("/")[-1] if "/" in url else url

    if not title and not abstract:
        return None

    return {
        "id": record_id,
        "url": url,
        "title": title or "(No title)",
        "abstract": abstract or "",
        "author": author or "Unknown",
        "year": year,
        "methodology": infer_methodology(title, abstract),
    }


def scrape_macs_theses(max_records: int | None = None) -> list[dict]:
    """Main scraper: fetch search pages, follow links, extract metadata."""
    LOGS_DIR.mkdir(exist_ok=True)
    seen_urls: set[str] = set()
    theses: list[dict] = []
    intermediate: list[dict] = []

    logger.info(f"Starting scrape: {SEARCH_URL}")

    with httpx.Client(
        limits=httpx.Limits(max_connections=5),
        headers={"User-Agent": "Mozilla/5.0 (compatible; MACSS-research/1.0)"},
        follow_redirects=True,
    ) as client:
        resp = fetch_with_retry(client, SEARCH_URL)
        if not resp:
            logger.error("Failed to fetch search page")
            return []

        record_urls = parse_search_page(resp.text, BASE_URL)
        logger.info(f"Found {len(record_urls)} record links")

        if not record_urls:
            for jrec in [26, 51]:
                paginated = f"{SEARCH_URL}&jrec={jrec}"
                r = fetch_with_retry(client, paginated)
                if r:
                    more = parse_search_page(r.text, BASE_URL)
                    for u in more:
                        if u not in seen_urls:
                            seen_urls.add(u)
                            record_urls.append(u)

        for rec_url in record_urls:
            if max_records and len(theses) >= max_records:
                break
            if rec_url in seen_urls:
                continue
            seen_urls.add(rec_url)

            time.sleep(REQUEST_DELAY)
            resp = fetch_with_retry(client, rec_url)
            if not resp:
                continue

            record = parse_record_page(resp.text, rec_url)
            if record:
                if not record.get("abstract") and len(record.get("title", "")) < 10:
                    continue
                theses.append(record)
                intermediate.append(record)
                logger.info(f"[{len(theses)}] {record.get('title', '')[:60]}... ({record.get('year')})")

            if len(intermediate) % 5 == 0 and intermediate:
                data = {
                    "source": "knowledge.uchicago.edu",
                    "collected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "theses": intermediate,
                }
                INTERMEDIATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return theses


def run_scrape(max_records: int = 50) -> Path:
    """Scrape theses and save to MACSS_PATH. Returns path to saved file."""
    theses = scrape_macs_theses(max_records=max_records)
    path = save_corpus(theses, MACSS_PATH)
    logger.info(f"Saved {len(theses)} theses to {path}")
    return path


# --- Details enrichment (Record Appears in, Keywords, Degree Type) ---

MACSS_MARKERS = ("computational social sciences", "macss")


def _find_detail_value(soup: BeautifulSoup, label_text: str) -> str:
    """Find a detail label (e.g. 'Keywords') and return the associated value text."""
    label_lower = label_text.lower()
    for tag in soup.find_all(string=lambda s: s and label_lower in (s.strip().lower() if isinstance(s, str) else "")):
        parent = tag.parent if hasattr(tag, "parent") else None
        if not parent:
            continue
        # Next sibling or parent's next sibling
        next_el = parent.find_next_sibling()
        if next_el:
            return next_el.get_text(separator=" ", strip=True)
        # dt/dd: we have the dt, get dd
        if parent.name == "dt":
            dd = parent.find_next_sibling("dd")
            if dd:
                return dd.get_text(separator=" ", strip=True)
        if parent.name == "th":
            td = parent.find_next_sibling("td")
            if td:
                return td.get_text(separator=" ", strip=True)
        # Try next element in parent
        for sib in parent.next_siblings:
            if hasattr(sib, "get_text"):
                return sib.get_text(separator=" ", strip=True)
    return ""


def _find_detail_links(soup: BeautifulSoup, label_text: str) -> list[str]:
    """Find a detail label and return list of link texts (e.g. for Record Appears in)."""
    label_lower = label_text.lower()
    for tag in soup.find_all(string=lambda s: s and label_lower in (s.strip().lower() if isinstance(s, str) else "")):
        parent = tag.parent if hasattr(tag, "parent") else None
        if not parent:
            continue
        container = parent.find_next_sibling() or parent.parent
        if not container:
            continue
        links = container.find_all("a", href=True)
        if links:
            return [a.get_text(strip=True) for a in links if a.get_text(strip=True)]
        # Single block of text with " > " separators
        text = container.get_text(separator=" ", strip=True)
        if ">" in text:
            return [s.strip() for s in text.replace("\n", " ").split("  ") if ">" in s or s.strip()]
        if text:
            return [text]
    return []


def _extract_abstract_from_soup(soup: BeautifulSoup) -> str:
    """Extract full abstract from record page (same logic as parse_record_page). Used during enrichment to prefer longer/full abstract."""
    abstract = ""
    for sel in [".abstract", ".description", "[class*='abstract']", "[class*='description']"]:
        el = soup.select_one(sel)
        if el:
            abstract = el.get_text(strip=True)
            if len(abstract) > 50:
                return abstract
    if not abstract:
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            abstract = meta["content"] or ""
    return abstract or ""


def enrich_thesis_from_record_page(html: str, url: str) -> dict:
    """Parse the Details section of a record page. Returns dict with keywords, record_appears_in, degree_type, primary_category, is_macss, and abstract_from_page when the page has a longer abstract than OAI."""
    soup = BeautifulSoup(html, "html.parser")
    result: dict = {
        "keywords": [],
        "record_appears_in": [],
        "degree_type": "",
        "primary_category": "",
        "is_macss": False,
    }

    # Record Appears in (list of hierarchy strings)
    record_entries = _find_detail_links(soup, "Record Appears in")
    if not record_entries:
        val = _find_detail_value(soup, "Record Appears in")
        if val:
            record_entries = [s.strip() for s in val.split("\n") if s.strip()]
    result["record_appears_in"] = record_entries

    # primary_category: last segment of first hierarchy (e.g. "Astronomy and Astrophysics")
    if record_entries:
        first = record_entries[0]
        result["primary_category"] = first.split(">")[-1].strip() if ">" in first else first

    # is_macss
    combined = " ".join(record_entries).lower()
    result["is_macss"] = any(m in combined for m in MACSS_MARKERS)

    # Keywords (comma-separated or list)
    kw_val = _find_detail_value(soup, "Keywords")
    if kw_val:
        result["keywords"] = [k.strip() for k in kw_val.replace(",", ";").split(";") if k.strip()]

    # Degree Type
    result["degree_type"] = _find_detail_value(soup, "Degree Type").strip()

    # Full abstract from record page (OAI may give truncated dc:description; use page abstract when longer)
    result["abstract_from_page"] = _extract_abstract_from_soup(soup)

    return result


def enrich_corpus(theses: list[dict], max_records: int | None = None) -> list[dict]:
    """Fetch each thesis record page and merge Details (keywords, record_appears_in, degree_type) into thesis dicts."""
    import httpx
    to_process = [t for t in theses if t.get("url")]
    if max_records is not None:
        to_process = to_process[:max_records]
    out = list(theses)
    url_to_idx = {t.get("url"): i for i, t in enumerate(theses) if t.get("url")}

    with httpx.Client(timeout=30.0, headers={"User-Agent": "Mozilla/5.0 (compatible; MACSS-research/1.0)"}) as client:
        for i, thesis in enumerate(to_process):
            url = thesis.get("url")
            if not url:
                continue
            time.sleep(REQUEST_DELAY)
            resp = fetch_with_retry(client, url)
            if not resp:
                logger.warning(f"Enrich skip (fetch failed): {url}")
                continue
            extra = enrich_thesis_from_record_page(resp.text, url)
            idx = url_to_idx.get(url)
            if idx is not None:
                merged = {**out[idx], **{k: v for k, v in extra.items() if k != "abstract_from_page"}}
                # Prefer full abstract from record page when it's longer than OAI dc:description
                page_abstract = (extra.get("abstract_from_page") or "").strip()
                current_abstract = (out[idx].get("abstract") or "").strip()
                if page_abstract and len(page_abstract) > len(current_abstract):
                    merged["abstract"] = page_abstract
                out[idx] = merged
            if (i + 1) % 5 == 0:
                logger.info(f"Enriched {i + 1}/{len(to_process)}")
    return out


def enrich_corpus_from_file(path: Path | None = None, max_records: int | None = None) -> Path:
    """Load corpus from MACSS_PATH, enrich each thesis via record page, save back. Returns path to saved file."""
    path = path or MACSS_PATH
    if not path.exists():
        logger.warning(f"Corpus not found at {path}; run fetch-corpus first.")
        return path
    data = json.loads(path.read_text(encoding="utf-8"))
    theses = data.get("theses", [])
    if not theses:
        logger.warning("No theses in corpus.")
        return path
    theses = enrich_corpus(theses, max_records=max_records)
    data["theses"] = theses
    data["enriched_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Saved enriched corpus ({len(theses)} theses) to {path}")
    return path
