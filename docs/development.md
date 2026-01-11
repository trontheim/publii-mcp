# Entwicklung

Anleitung für die Entwicklung am publii-mcp Projekt.

## Voraussetzungen

- Python >=3.10 (via asdf: `asdf install python 3.12.0`)
- uv (Package Manager)
- Publii CMS (für Integrationstests)

## Setup

```bash
# Repository klonen
git clone <repo-url>
cd publii-mcp

# Abhängigkeiten installieren
uv sync

# Entwicklungsumgebung aktivieren
source .venv/bin/activate
```

## Projektstruktur

```
publii-mcp/
├── src/publii_mcp/
│   ├── __init__.py      # Version-Export
│   ├── cli.py           # Typer CLI (serve, info)
│   ├── db.py            # SQLite-Abstraktion
│   └── server.py        # FastMCP Server
├── tests/
│   └── test_db.py       # Unit-Tests
├── docs/
│   ├── api.md           # API-Referenz
│   └── development.md   # Diese Datei
├── pyproject.toml       # Projekt-Konfiguration
└── README.md
```

## Tests

```bash
# Alle Tests ausführen
pytest

# Mit Coverage-Report
pytest --cov

# Nur bestimmte Tests
pytest tests/test_db.py::TestPubliiDB::test_list_posts

# Verbose Output
pytest -v
```

### Test-Struktur

Die Tests verwenden pytest Fixtures für temporäre Publii-Verzeichnisse:

- `TestPubliiDB` - Core DB-Operationen (16 Tests)
- `TestPubliiDBPages` - Page-spezifische Tests (3 Tests)
- `TestPubliiDBTagsAuthors` - Metadata-Tests (2 Tests)

## Code-Qualität

### Ruff (Linter & Formatter)

```bash
# Lint-Fehler anzeigen
ruff check .

# Lint-Fehler automatisch beheben
ruff check --fix .

# Code formatieren
ruff format .

# Beides zusammen
ruff check --fix . && ruff format .
```

### Konfigurierte Regeln

Aus `pyproject.toml`:

- `E` - pycodestyle errors
- `F` - pyflakes
- `I` - isort (Import-Sortierung)
- `UP` - pyupgrade
- `B` - flake8-bugbear
- `SIM` - flake8-simplify

**Ausnahmen:**
- `B008` - Für Typer's `Option()` Pattern
- Zeilenlänge: 100 Zeichen (120 für SQL-Strings in Tests)

## Architektur

### Schichten

1. **CLI Layer** (`cli.py`)
   - Typer-basiert
   - Befehle: `serve`, `info`
   - Rich für formatierte Ausgabe

2. **Server Layer** (`server.py`)
   - FastMCP Framework
   - 14 Tools via `@mcp.tool` Decorator
   - Globale DB-Instanz (`_db`)

3. **Database Layer** (`db.py`)
   - `PubliiDB` Klasse
   - Direkte SQLite-Queries (kein ORM)
   - Multi-Site-Support

### Wichtige Patterns

**Draft-first:** Neue Posts/Pages sind standardmäßig Entwürfe
```python
status = status or "draft"
```

**Auto-Slug:** Slugs werden aus Titeln generiert
```python
slug = slug or self._generate_slug(title)
```

**Status-Suffix:** Pages verwenden `"<status>,is-page"` Format
```python
db_status = f"{status},is-page"
```

## Neues Tool hinzufügen

1. **DB-Methode** in `db.py`:
```python
def my_new_method(self, site: str | None = None) -> list[dict]:
    """Docstring."""
    db_path = self._get_db_path(site)
    # SQLite-Logik
    return result
```

2. **MCP-Tool** in `server.py`:
```python
@mcp.tool
def my_new_tool(site: str | None = None) -> list[dict]:
    """Tool-Beschreibung für MCP-Client."""
    return _db.my_new_method(site)
```

3. **Tests** in `test_db.py`:
```python
def test_my_new_method(self, temp_publii_dir: Path) -> None:
    db = PubliiDB(temp_publii_dir, default_site="test-site")
    result = db.my_new_method()
    assert ...
```

4. **Dokumentation** in `docs/api.md` aktualisieren

## Debugging

```bash
# Server im Debug-Modus
publii-mcp serve --site test-site 2>&1 | tee debug.log

# SQLite direkt inspizieren
sqlite3 ~/Documents/Publii/sites/<site>/input/db.sqlite ".schema"
```

## Release

1. Version in `pyproject.toml` und `__init__.py` aktualisieren
2. Tests und Linting ausführen
3. Git-Tag erstellen: `git tag v1.x.x`
4. Build: `uv build`
