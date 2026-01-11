# publii-mcp

MCP Server für Publii CMS. Ermöglicht Claude Code und anderen MCP-Clients die Interaktion mit Publii-Websites.

## Voraussetzungen

- **Python:** >=3.10
- **Publii:** Installiert mit mindestens einer Site
- **Verzeichnisstruktur:** Publii speichert Sites unter `~/Documents/Publii/sites/<site-name>/input/db.sqlite`

## Installation

```bash
uv tool install .
```

## Nutzung

```bash
# Server starten
publii-mcp serve

# Mit spezifischer Site
publii-mcp serve --site meine-site

# Mit benutzerdefiniertem Datenverzeichnis
publii-mcp serve --data-dir /pfad/zu/publii

# Verfügbare Sites anzeigen
publii-mcp info
```

## Features

- **14 MCP Tools** für Posts, Pages, Tags und Authors
- **Multi-Site Support** - Arbeite mit mehreren Publii-Sites
- **Draft-first Workflow** - Neue Posts/Pages werden standardmäßig als Entwurf erstellt
- **Automatische Slug-Generierung** - URL-freundliche Slugs aus Titeln (inkl. Umlaut-Konvertierung: ä→ae, ö→oe, ü→ue, ß→ss)

### Draft-first Workflow

Beim Erstellen von Posts oder Pages wird der Status standardmäßig auf `draft` gesetzt. Dies verhindert versehentliche Veröffentlichungen und ermöglicht eine Überprüfung vor der Publikation:

```
create_post("Mein Titel", "Inhalt...")  # Status: draft
create_post("Mein Titel", "Inhalt...", status="published")  # Sofort veröffentlicht
```

### Automatische Slug-Generierung

Wenn kein Slug angegeben wird, generiert das System automatisch einen URL-freundlichen Slug aus dem Titel:

- `"Mein erster Artikel"` → `mein-erster-artikel`
- `"Über uns"` → `ueber-uns`
- `"Größe & Maße"` → `groesse-masse`

## MCP Tools Übersicht

| Kategorie | Tools | Beschreibung |
|-----------|-------|--------------|
| Sites | `list_sites`, `get_site_info` | Sites auflisten und Details abrufen |
| Posts | `list_posts`, `get_post`, `create_post`, `update_post`, `delete_post` | Blog-Beiträge verwalten |
| Pages | `list_pages`, `get_page`, `create_page`, `update_page`, `delete_page` | Statische Seiten verwalten |
| Metadata | `list_tags`, `list_authors` | Tags und Autoren abrufen |

Siehe [docs/api.md](docs/api.md) für die vollständige API-Referenz.

## Fehlerbehandlung

Das System wirft `ValueError` bei folgenden Situationen:

| Fehler | Ursache |
|--------|---------|
| `"Keine Site angegeben und kein Default gesetzt"` | Weder `--site` Parameter noch Default-Site konfiguriert |
| `"Site nicht gefunden: <name>"` | Die angegebene Site existiert nicht |
| `"Post nicht gefunden: <id>"` | Post mit der ID existiert nicht |
| `"Page nicht gefunden: <id>"` | Page mit der ID existiert nicht |
| `"Autor nicht gefunden: <id>"` | Ungültige Author-ID beim Erstellen |

## Entwicklung

Siehe [docs/development.md](docs/development.md) für Setup-Anweisungen.

```bash
# Tests ausführen
pytest

# Mit Coverage
pytest --cov

# Code formatieren und linten
ruff check --fix .
ruff format .
```

## Lizenz

MIT
