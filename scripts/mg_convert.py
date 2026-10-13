"""Madagascar: convert the Assemblée nationale texts to Markdown.
French versions ("VF") go to fr/, Malagasy versions ("VM") to mg/. Word files are converted with macOS textutil,
PDFs with poppler pdftotext; scans without a text layer are skipped (no OCR).
Usage: python mg_convert.py <repo_dir>"""
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mg_text import pdf_text, doc_text, clean_pages, structure, write_md, slug, text_quality, sniff  # noqa: E402

RAW = os.environ.get("MG_RAW", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "mg"))
TODAY = datetime.date.today().isoformat()
DIRS = {"CT": "constitution", "RI": "reglement-interieur", "LO": "lois-organiques", "LF": "lois-de-finances",
        "LFR": "lois-de-finances", "LR": "lois-de-reglement", "LP": "lois", "LOO": "lois", "PL": "lois",
        "TI": "lois-autorisant-ratification", "LH": "lois-habilitation", "OR": "ordonnances"}
TYPES = {"CT": "constitution", "RI": "regulation", "OR": "ordinance"}


def text_of(path):
    k = sniff(path)
    if k == "pdf":
        pages, _ = pdf_text(path)
        return pages
    if k in ("doc", "docx", "rtf"):
        src = path
        ext = "." + k
        if not path.lower().endswith(ext):
            src = path + ext
            if not os.path.exists(src):
                os.link(path, src)
        return doc_text(src)
    return []


def lang_of(text, version):
    if version and ("VM" in version or "Malagasy" in version):
        return "mg"
    t = text[:20000].lower()
    mg = len(re.findall(r"\b(ny|sy|amin'ny|izay|dia|ary|ho|tsy)\b", t))
    fr = len(re.findall(r"\b(le|la|les|des|du|est|qui|dans)\b", t))
    return "mg" if mg > fr else "fr"


def main(repo):
    items = json.load(open(os.path.join(RAW, "index.json")))
    n = skipped = 0
    hashes, seen = set(), set()
    for it in items:
        cat = it.get("categorie") or ("CT" if it["title"].startswith("CT-") else "RI" if it["title"].startswith("RI-")
                                      else "TI" if "ratification" in it["title"].lower() else "LOO")
        num = it.get("numero", "")
        if not re.search(r"\d", num):
            num = ""
        m = re.search(r"(?:n\s*°|n°|N°)\s*(\d{2,4}\s*[-–/]\s*\d{2,3})", it["title"])
        if not num and m:
            num = re.sub(r"\s", "", m.group(1)).replace("–", "-")
        if not num:
            m = re.search(r"\b((?:19|20)\d\d)\s*[-–]\s*(\d{3})\b", it["title"])
            num = "%s-%s" % (m.group(1), m.group(2)) if m else ""
        for fl in it.get("files", []):
            f = fl.get("file")
            if not f:
                continue
            pages = text_of(f)
            full = "\n".join(pages)
            if len(re.sub(r"\s", "", full)) < 400 or text_quality(full) < 0.7:
                print("SKIP (no usable text)", os.path.basename(f))
                skipped += 1
                continue
            h = hashlib.sha1(full.encode()).hexdigest()
            if h in hashes:
                continue
            hashes.add(h)
            lang = lang_of(full, fl.get("version", ""))
            title = re.sub(r"\s+", " ", it["title"]).strip()
            title = re.sub(r"^(\d{4}-\d{3}|CT-\d{4}|RI-AN)\s*-\s*", "", title)
            year = it.get("year") or (re.search(r"\b(19|20)\d\d\b", num + " " + title) or re.search("()", "")).group(0)
            if cat in ("CT", "RI"):
                name = slug(title)
            else:
                name = ("loi-" + num + "-" if num and re.match(r"\d", num) else "") + slug(re.sub(r"(?i)^loi\s+(n\s*°|n°)?\s*[\d\s\-–/]+", "", title))[:80]
            path = os.path.join(repo, lang, DIRS.get(cat, "lois"), (year or "sans-date") if cat not in ("CT", "RI") else "", name + ".md")
            path = os.path.normpath(path)
            if path in seen:
                path = path[:-3] + "-2.md"
            seen.add(path)
            body = structure(clean_pages(pages), "fr")
            meta = {"title": title, "identifier": ("Loi n° " + num) if num and cat not in ("CT", "RI", "OR") else num,
                    "type": TYPES.get(cat, "law"), "jurisdiction": "mg", "language": lang, "year": year,
                    "status": "unknown", "source": fl["url"], "retrieved": TODAY,
                    "note": "Assemblée nationale de Madagascar — %s (%s)" % (it.get("categorie_label") or "texte promulgué", it["origin"])}
            write_md(path, meta, title, body)
            n += 1
    print("written", n, "skipped", skipped)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
