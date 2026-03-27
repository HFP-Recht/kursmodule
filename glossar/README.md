# Glossar Sources

This folder contains glossary sources used by `build_portal.py`.

## 1) Keyword config

`keywords.json` defines which terms should be linkified in the portal and which glossary page each term points to.

Schema:

```json
{
  "terms": [
    {
      "term": "Nichtigkeit",
      "page": "nichtigkeit.html",
      "modules": ["04-vertragsformen"],
      "aliases": ["nichtig"],
      "short": "Der Vertrag ist von Anfang an rechtlich unwirksam.",
      "definition": "Optional override shown in popover"
    }
  ]
}
```

Notes:
- `modules` is optional. If omitted, the term is active globally.
- `aliases` is optional. Aliases link to the same page.
- `definition` is optional. If omitted, the popover uses the first sentence from the page HTML.

## 2) Term pages

Each term has its own page in this same folder, e.g. `nichtigkeit.html`.
On second click, users open that page from the portal.
