"""Madagascar: list and download legislative texts published by the Assemblée nationale de Madagascar
(https://www.assemblee-nationale.mg, open data under Licence Ouverte 2.0).

1. /textes/?status=ARCHIVE&categorie=<CAT>&per_page=100&page=N — the archive table (number, title, category,
   year, file links "VF" = French version, "VM" = Malagasy version) for the categories:
   CT Constitution, RI Règlement intérieur, LOO Loi ordinaire, LO Loi organique, LF Loi de finances,
   LFR Loi de finances rectificative, LR Loi de règlement, LP Loi de programme, TI Traité international
   (laws authorising ratification), LH Loi d'habilitation, OR Ordonnance.
   PL "Projet de loi" — only the entries that are adopted laws ("Loi n° ...") are kept.
   (Bills, resolutions, minutes and analytical reports are not collected.)
2. /textes/?status=PROMULGATION — recently promulgated laws (text pages link the file).
Files (PDF or Word) are hosted on the Assembly's file storage (r2.dev). The /opendata/api/ endpoints are
disallowed in robots.txt and were not used. Cache: _raw/mg/. Usage: python mg_fetch.py
"""
import html
import json
import os
import re
import sys
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mg_text import fetch, pdf_ok, sniff  # noqa: E402

BASE = "https://www.assemblee-nationale.mg"
RAW = os.environ.get("MG_RAW", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "mg"))
CATS = ["CT", "RI", "LOO", "LO", "LF", "LFR", "LR", "LP", "TI", "LH", "OR", "PL"]
DELAY = 3.0
R2 = r'https://pub-[0-9a-f]+\.r2\.dev/[^"]+'


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def get(url, name):
    p = fetch(url, os.path.join(RAW, "html", name), delay=DELAY)
    return open(p, encoding="utf-8", errors="replace").read() if p else ""


def archive():
    items = []
    for cat in CATS:
        pg = 1
        while True:
            h = get("%s/textes/?status=ARCHIVE&categorie=%s&per_page=100&page=%d" % (BASE, cat, pg), "arch-%s-%d.html" % (cat, pg))
            rows = re.findall(r"<tr>\s*<td class=\"archive-numero\">(.*?)</tr>", h, re.S)
            for r in rows:
                num = text(r.split("</td>", 1)[0])
                m = re.search(r'class="archive-titre" title="([^"]*)"', r)
                cats = re.search(r'class="archive-categorie">(.*?)</td>', r, re.S)
                year = re.search(r'class="archive-annee">(.*?)</td>', r, re.S)
                title = html.unescape(m.group(1)) if m else ""
                if cat == "PL" and not re.match(r"(?i)\s*(loi|ordonnance)\b", title):
                    continue  # bills ("Projet de loi ...") are not collected; adopted laws filed under PL are
                files = re.findall(r'<a href="(%s)"[^>]*class="archive-pdf-link" title="([^"]*)"' % R2, r)
                items.append({"numero": num, "title": html.unescape(m.group(1)) if m else "", "categorie": cat,
                              "categorie_label": text(cats.group(1)) if cats else "", "year": text(year.group(1)) if year else "",
                              "files": [{"url": html.unescape(u), "version": v} for u, v in files], "origin": "archive"})
            if not rows or "page=%d&" % (pg + 1) not in html.unescape(h):
                break
            pg += 1
    return items


def promulgation():
    items, seen = [], set()
    pg = 1
    while True:
        h = get("%s/textes/?status=PROMULGATION&sort=-date_depot&per_page=8&page=%d" % (BASE, pg), "prom-%d.html" % pg)
        new = 0
        for u, t in re.findall(r'<a[^>]+href="(/textes/[^"?#]+/)"[^>]*>(.*?)</a>', h, re.S):
            t = text(t)
            if u in seen or not t or t == "Voir les détails":
                continue
            seen.add(u)
            new += 1
            items.append({"page": BASE + u, "title": t, "origin": "promulgation"})
        if not new or "page=%d&" % (pg + 1) not in html.unescape(h):
            break
        pg += 1
    for k, it in enumerate(items):
        h = get(it["page"], "prom-text-%03d.html" % k)
        it["files"] = [{"url": html.unescape(u), "version": "VF" if re.search(r"_FR\.|VF", u) else ""}
                       for u in sorted(set(re.findall(r'href="(%s)"' % R2, h)))]
    return items


def main():
    items = archive() + promulgation()
    for it in items:
        for fl in it["files"]:
            name = re.sub(r"[^A-Za-z0-9.]+", "_", unquote(fl["url"].split(".r2.dev/", 1)[1]))[-150:]
            dest = os.path.join(RAW, "files", name)
            ok = fetch(fl["url"], dest, delay=DELAY, timeout=300, check_pdf=dest.lower().endswith(".pdf"))
            fl["file"] = ok
            if not ok:
                print("FAILED", fl["url"])
    json.dump(items, open(os.path.join(RAW, "index.json"), "w"), indent=1, ensure_ascii=False)
    print("items", len(items), "files", sum(len(i["files"]) for i in items))


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    main()
