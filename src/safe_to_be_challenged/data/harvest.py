"""OAI-PMH harvester for Knowledge UChicago."""
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

from ..config import BASE_URL, LOGS_DIR, MACSS_PATH, OAI_URL, REQUEST_DELAY
from .corpus import extract_year, infer_methodology, save_corpus, setup_logging

NS = {"oai": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/"}
DC_NS = "http://purl.org/dc/elements/1.1/"

logger = setup_logging()


def _extract_dc_text(dc_elem: ET.Element, tag: str) -> str:
    """Extract first non-empty text from dc element."""
    for e in dc_elem.findall(f".//{{{DC_NS}}}{tag}"):
        if e.text:
            return e.text.strip()
    return ""


def _extract_url(dc_elem: ET.Element) -> str:
    """Extract record URL from dc identifiers."""
    for ie in dc_elem.findall(f".//{{{DC_NS}}}identifier"):
        t = (ie.text or "").strip()
        if "knowledge.uchicago.edu" in t or "record" in t:
            return t if t.startswith("http") else f"{BASE_URL}/record/{t.split('/')[-1].split(':')[-1]}"
        if "doi:" in t:
            return f"https://doi.org/{t.replace('doi:', '')}"
    return ""


def parse_oai_record(rec: ET.Element) -> dict | None:
    """Parse a single OAI record element into thesis dict."""
    header = rec.find("oai:header", NS)
    meta = rec.find("oai:metadata", NS)
    if header is None or meta is None:
        return None
    if header.get("status") == "deleted":
        return None

    dc = meta.find(f".//{{{DC_NS}}}dc")
    if dc is None and len(meta) > 0:
        dc = meta[0]
    if dc is None:
        return None

    title = _extract_dc_text(dc, "title")
    desc = _extract_dc_text(dc, "description")
    creator = _extract_dc_text(dc, "creator")
    url = _extract_url(dc)

    if not title and not desc:
        return None

    oai_id_elem = header.find("oai:identifier", NS)
    oai_id_text = oai_id_elem.text if oai_id_elem is not None else ""
    rec_id = oai_id_text.split(":")[-1] if ":" in oai_id_text else ""

    datestamp_elem = header.find("oai:datestamp", NS)
    datestamp = datestamp_elem.text if datestamp_elem is not None else ""
    year = extract_year(desc) or extract_year(title) or extract_year(datestamp)

    return {
        "id": rec_id,
        "url": url or f"{BASE_URL}/record/{rec_id}",
        "title": title or "(No title)",
        "abstract": desc or "",
        "author": creator or "Unknown",
        "year": year,
        "methodology": infer_methodology(title, desc),
    }


def harvest_theses(max_records: int = 50, *, oai_url: str = OAI_URL) -> list[dict]:
    """Harvest thesis records via OAI-PMH ListRecords."""
    LOGS_DIR.mkdir(exist_ok=True)
    theses: list[dict] = []
    token: str | None = None
    initial_params = {"verb": "ListRecords", "metadataPrefix": "oai_dc", "set": "Theses"}

    with httpx.Client(timeout=60.0) as client:
        while len(theses) < max_records:
            params = {"verb": "ListRecords", "resumptionToken": token} if token else initial_params
            r = client.get(oai_url, params=params)
            r.raise_for_status()
            root = ET.fromstring(r.content)

            for rec in root.findall(".//oai:record", NS):
                parsed = parse_oai_record(rec)
                if parsed:
                    theses.append(parsed)
                    logger.info(f"[{len(theses)}] {parsed['title'][:50]}... ({parsed['year']})")
                if len(theses) >= max_records:
                    break

            res = root.find(".//oai:resumptionToken", NS)
            if res is None or not res.text:
                break
            token = res.text
            time.sleep(REQUEST_DELAY)

    return theses


def run_harvest(max_records: int = 50) -> Path:
    """Harvest theses and save to MACSS_PATH. Returns path to saved file."""
    theses = harvest_theses(max_records=max_records)
    path = save_corpus(theses, MACSS_PATH, harvest_method="oai-pmh")
    logger.info(f"Saved {len(theses)} theses to {path}")
    return path
