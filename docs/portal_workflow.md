# Portal Workflow (Technische Dokumentation)

## 1) Zielbild

Das Repository erzeugt ein statisches Lernportal als `index.html`, ergänzt durch lokale Gesetzesseiten im Ordner `laws/`.

Ergebnis:

- Online nutzbar über GitHub Pages
- Offline nutzbar über ein automatisch erzeugtes ZIP-Paket
- Keine Serverlogik nötig (reines Static Hosting)

---

## 2) Inhaltsquellen und Ordnerstruktur

### 2.1 Modulordner

Die Module liegen in Ordnern wie:

- `01_Schweizer Rechtsystem`
- `02_Personenrecht`
- …

Pro Modul können vorkommen:

- `*.md` (Lerninhalt mit Callouts/Mermaid)
- `*.json` (Fragen, Fallstudien, Checklisten, Glossar)
- `*.html` (bestehende Zusammenfassungen/Kompetenz-Checks)

### 2.2 Gesetze

- Quell-XML: `Gesetze/*.xml`
- Generierte Offline-Gesetze: `laws/*.html`

Optional:

- `law_summaries.json` für Kurz-Zusammenfassungen je Artikel.

---

## 3) Build-Prozess in `build_portal.py`

Entry Point:

- `build_portal(root_dir)` (ab Zeile ~1766)

### 3.1 Ablaufübersicht

1. `prepare_local_laws(root)` erzeugt aus XML lokale Gesetzes-HTML-Dateien.
2. Modulordner werden erkannt (ausser `Gesetze`, `laws`, versteckte Ordner).
3. Pro Modul werden Inhalte aus MD/JSON/HTML geladen.
4. Modul-HTML und Navigation werden zusammengesetzt.
5. `HTML_TEMPLATE` wird mit Platzhaltern gefüllt.
6. Ergebnis wird als `index.html` geschrieben.

### 3.2 Wichtige Parser/Loader

- `parse_md(...)`:
  - Liest Titel, `###`-Abschnitte und extrahiert strukturierte Items.
- `extract_items(...)`:
  - Unterstützt Callouts (`info`, `leitsatz/merksatz`, `pitfall/achtung`)
  - Extrahiert Mermaid-Blöcke
  - Unbekannte Callout-Typen werden bewusst konsumiert/verworfen (verhindert Leaks kaputter Inhalte).
- `load_jsons(...)`:
  - Ermittelt Datentypen über `type` / `subAssignments`:
    - Fragen (`quill`)
    - Fallstudien (`law_case`)
    - Checklisten (`checkliste`)
    - Glossar (`type=glossar`)
- `load_html_files(...)`:
  - Bindet zusätzliche HTML-Dateien pro Modul ein (ausser `portal.html`).

### 3.3 Rendering

- `render_module(...)` baut je Modul:
  - Header
  - Lerninhalt (MD)
  - „Das Wichtigste in Kürze“ (HTML-Blöcke)
  - Verständnisfragen
  - Fallstudien
  - Checklisten
  - Glossar

---

## 4) Gesetzes-XML zu offline suchbaren Gesetzen

### 4.1 Konvertierung

Zentrale Funktionen:

- `build_law_html(xml_path, out_dir)`
- `prepare_local_laws(root)`

Die XML-Dateien werden geparst (AKN/LegalDocML), Artikel extrahiert und zu lokalem HTML geschrieben.

### 4.2 Lokale Link-Umschreibung

Funktionen wie:

- `_localize_law_href(...)`
- `_rewrite_markdown_links(...)`
- `_rewrite_law_hrefs_in_html(...)`
- `_link_plain_law_refs(...)`

ersetzen externe Fedlex/admin.ch-Referenzen durch lokale `laws/*.html#art_x` Links.

### 4.3 Such-/Preview-Daten

Während der Gesetzeskonvertierung entsteht `LAW_PREVIEW_DATA`:

- Schlüssel: `laws/<gesetz>.html#art_*`
- Inhalt: Gesetz, Artikeltitel, Textauszug, optionale Zusammenfassung

Diese Daten landen als JSON im Frontend (`LAW_PREVIEW_PLACEHOLDER`) und ermöglichen:

- Gesetzestreffer in der Portalsuche
- Vorschau-Popover beim ersten Klick auf Gesetzeslinks

---

## 5) Struktur der generierten `index.html`

`HTML_TEMPLATE` definiert:

- Header (`#header`)
- Sidebar-Navigation (`#sidebar`)
- Hauptbereich (`#main`, `#content`)
- Print-Modal
- Eingebettete Styles + JavaScript

Platzhalter:

- `NAVLIST_PLACEHOLDER`
- `CONTENT_PLACEHOLDER`
- `LAW_PREVIEW_PLACEHOLDER`

### 5.1 Wichtige Frontend-Funktionen

- Scrollspy für aktive Navigation
- Volltextsuche mit Treffer-Navigation (`Enter`, `Shift+Enter`)
- Gesetzes-Suchspalte inkl. Preview
- Print-Auswahl nach Modulen/Inhaltstypen
- Lernmodus („Antworten ausblenden“):
  - JSON-Antworten (`.qa-answer`, `.step-solution`, `.disc-a`)
  - HTML-Kompetenz-Checks (`.dropdown-content .answer`)

---

## 6) Laufender Inhaltspfad (Autor:innen-Workflow)

1. Neue/aktualisierte Inhalte in Modulordnern ablegen (`.md`, `.json`, `.html`).
2. Optional: neue Gesetzes-XML in `Gesetze/` ablegen.
3. Lokal bauen:

```bash
python build_portal.py
```

4. `index.html` (und ggf. `laws/`) committen.
5. Push auf `main`.

---

## 7) Deployment auf GitHub Pages

Workflow:

- `.github/workflows/pages-static.yml`

Trigger:

- Push auf `main`

Ablauf:

1. Checkout
2. `_site/` erstellen
3. `index.html` nach `_site/index.html`
4. `laws/` nach `_site/laws`
5. Artifact hochladen
6. Deployment via `actions/deploy-pages`

Ziel-URL:

- `https://hfp-recht.github.io/kursmodule/`

---

## 8) Offline-ZIP (automatisch aktualisiert)

Workflow:

- `.github/workflows/offline-zip-release.yml`

Trigger:

- Push auf `main`

Ablauf:

1. `dist/offline/` erzeugen
2. `index.html` + `laws/` hinein kopieren
3. ZIP erstellen: `dist/hfp-offline.zip`
4. Release-Asset unter Tag `offline-latest` ersetzen

Stabiler Download-Link:

- `https://github.com/HFP-Recht/kursmodule/releases/latest/download/hfp-offline.zip`

Offline-Nutzung:

1. ZIP herunterladen
2. Entpacken
3. `offline/index.html` lokal öffnen

---

## 9) Zukunft: Erweiterungen (Glossar, neue Inhaltstypen, UX)

### 9.1 Glossar-Weiterentwicklung

Aktuell wird `type=glossar` bereits erkannt und gerendert.
Mögliche nächste Schritte:

- Alphabetischer Index je Modul + global
- Glossar-Synonyme
- Glossar in der Hauptsuche priorisieren
- Crosslinks aus Lerntexten auf Glossarbegriffe

### 9.2 Neue JSON-Inhaltstypen

Vorgehen:

1. `load_jsons(...)` um neuen Typ erweitern
2. Renderer ergänzen
3. `render_module(...)` einhängen
4. Nav-Unterpunkte ergänzen
5. Optional Lernmodus/Print-Sicht berücksichtigen

### 9.3 Frontend/Interaktion

Mögliche Roadmap:

- Persistente Nutzerpräferenzen (Lernmodus, geöffnete Sektionen)
- Bessere Mobile-Navigation
- Verbesserte Drucktemplates je Blocktyp

---

## 10) Zukunft: Optionales Vercel-Hosting

Da die Ausgabe statisch ist, ist Vercel unkompliziert:

1. Repository in Vercel importieren
2. Framework Preset: `Other`
3. Build Command: leer (wenn `index.html` bereits committed)
4. Output Directory: `.`

Alternativ mit Build in Vercel:

- Build Command: `python build_portal.py`
- Dann `index.html` als Root-Entry ausliefern

Hinweis:

- Für konsistentes Ergebnis sollte nur **eine** Pipeline als „Source of Truth“ genutzt werden (GitHub Actions oder Vercel Build), nicht beides gleichzeitig.

---

## 11) Wartung und Troubleshooting

### 11.1 Typische Fehlerquellen

- Gesetzeslink zeigt extern statt lokal:
  - Prüfen, ob XML in `Gesetze/` vorhanden und `laws/*.html` frisch generiert wurde.
- Fehlender Inhalt im Modul:
  - Dateityp und JSON-`type`/`subAssignments` prüfen.
- Mermaid-Diagramme fehlen:
  - Syntax in Markdown und Blockgrenzen prüfen.

### 11.2 Nach jeder strukturellen Änderung prüfen

- Build lokal: `python build_portal.py`
- Startseite öffnet (`index.html`)
- Suche + Lernmodus + Print funktionieren
- Gesetzeslinks und Popover funktionieren
- ZIP-Download-Link ist erreichbar (nach Workflowlauf)

