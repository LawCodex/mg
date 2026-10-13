# Madagascar (MG) — législation en Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Laws of the Republic of Madagascar adopted by Parliament, mainly in **French** (`fr/`), with the **Malagasy**
version where the Assemblée nationale publishes one (`mg/`), from the **Assemblée nationale de Madagascar** text
archive (https://www.assemblee-nationale.mg/textes/), published under the *Licence Ouverte / Open Licence v2.0*.
Texts are as adopted/promulgated (not consolidated). Retrieved 2026-10-13.

| Category | fr | mg |
|---|---|---|
| Constitution (IVe République, 2010) | 1 | – |
| Règlement intérieur de l'Assemblée nationale | 1 | – |
| Lois (ordinary laws, 1993–2026) | 543 | 32 |
| Lois autorisant la ratification (treaties, loan agreements) | 193 | 37 |
| Lois organiques | 19 | – |
| Lois de finances (initiales et rectificatives) | 11 | 7 |
| Lois d'habilitation | 3 | – |
| Ordonnances | 17 | 2 |
| **Total** | **788** | **78** |

## Structure

```
fr/constitution/constitution-de-la-iveme-republique.md
fr/reglement-interieur/
fr/lois/<year>/loi-<number>-<slug>.md
fr/lois-autorisant-ratification/<year>/   fr/lois-organiques/<year>/   fr/lois-de-finances/<year>/
fr/lois-habilitation/<year>/   fr/ordonnances/<year>/
mg/...                                     same layout for the Malagasy versions
```

Front matter: `identifier` (`Loi n° 2026-015`), `year`, `language` (`fr`/`mg`), `status: unknown`, `source` (file
URL on the Assembly's file storage), `note` (archive category). Word files were converted with macOS `textutil`,
PDFs with poppler `pdftotext`; TITRE / CHAPITRE / SECTION become headings and articles `Article N` headings
(French texts). Texts usually start with the *exposé des motifs*, followed by the law itself.

## Not covered / known gaps

* Coverage follows the Assembly's archive: many laws before 2010 and some years (e.g. 2009–2010, 2021–2025) are
  thinly represented. Decrees, orders and other regulatory texts of the Government are not included (the
  *Journal officiel* is not available as open data).
* Bills that were not adopted ("Projet de loi", "Proposition de loi"), resolutions, minutes and analytical
  reports were not collected. The Assembly's `/opendata/api/` endpoints are disallowed in robots.txt and were not
  used; the public HTML archive pages were used instead.
* One PDF without a text layer was skipped (Loi n° 97-032).
* Titles are as given by the Assembly's archive (some are abbreviated there).

## Sources and licence

| Source | URL |
|---|---|
| Assemblée nationale — Textes (archives, promulgation) | https://www.assemblee-nationale.mg/textes/?status=ARCHIVE |
| Licence Ouverte v2.0 | https://www.assemblee-nationale.mg/opendata/licence/ |

Reuse is allowed under the Licence Ouverte 2.0 with attribution: *Source : Assemblée Nationale de Madagascar —
parlement.mg, données mises à jour au 13 octobre 2026.* Downloads used an identifying User-Agent, one request every
3 seconds.

## Regenerate

```
pip install -r scripts/requirements.txt     # plus poppler (pdftotext) and macOS textutil (for .doc files)
python scripts/mg_fetch.py                  # downloads into ../_raw/mg/
python scripts/mg_convert.py .
```
