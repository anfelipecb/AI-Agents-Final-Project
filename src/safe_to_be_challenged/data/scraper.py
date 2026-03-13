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
