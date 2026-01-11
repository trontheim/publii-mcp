# Contributing to publii-mcp

Vielen Dank für dein Interesse, zu publii-mcp beizutragen! 🎉

## Entwicklungsumgebung einrichten

### Voraussetzungen

- **Python:** >=3.10 (empfohlen: 3.13+)
- **uv:** [Installation](https://github.com/astral-sh/uv)
- **Publii:** Installiert mit mindestens einer Test-Site
- **Git:** Für Version Control

### Setup

```bash
# Repository klonen
git clone https://github.com/trontheim/publii-mcp.git
cd publii-mcp

# Dependencies installieren (inkl. Dev-Dependencies)
uv sync --all-groups

# Pre-Commit Hooks einrichten (optional)
uv run pre-commit install
```

### Entwicklungs-Workflow

```bash
# Code-Änderungen vornehmen
# ...

# Linting und Formatting
uv run ruff check --fix .
uv run ruff format .

# Tests ausführen
uv run pytest

# Coverage-Report
uv run pytest --cov=src/publii_mcp --cov-report=html
open htmlcov/index.html
```

## Code-Konventionen

### Python-Style

Wir folgen **PEP 8** mit einigen Anpassungen via Ruff:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["B008"]  # Typer verwendet dieses Muster
```

**Key Rules:**
- **Line Length:** Max 100 Zeichen
- **Type Hints:** Verwende moderne Union-Syntax (`str | None` statt `Optional[str]`)
- **Imports:** Automatisch sortiert mit isort
- **Docstrings:** Deutsche Dokumentation für öffentliche APIs

### Beispiel

```python
def create_post(
    self,
    title: str,
    text: str,
    author_id: int,
    status: str = "draft",
    slug: str | None = None,
) -> dict:
    """Erstellt einen neuen Post.

    Args:
        title: Post-Titel
        text: Post-Content (HTML oder Markdown)
        author_id: Autor-ID (siehe list_authors)
        status: Status (draft, published, hidden, trashed)
        slug: URL-Slug (auto-generiert falls None)

    Returns:
        Dict mit Post-Daten inkl. ID

    Raises:
        ValueError: Bei ungültigem Status oder Autor
    """
    # Implementation
```

## Testing

### Test-Struktur

```
tests/
├── test_db.py           # PubliiDB Unit-Tests
├── test_cli.py          # CLI Tests (TODO)
└── test_server.py       # MCP Server Tests (TODO)
```

### Neuen Test schreiben

```python
import pytest
from publii_mcp.db import PubliiDB

class TestNewFeature:
    def test_something(self, temp_publii_dir):
        """Test neue Feature-Beschreibung."""
        db = PubliiDB(data_dir=temp_publii_dir, site="test-site")

        # Test-Code
        result = db.some_method()

        assert result == expected_value
```

### Fixtures

Verfügbare Fixtures in `tests/test_db.py`:

- `temp_publii_dir`: Temporäres Publii-Verzeichnis mit Schema
- `db_instance`: Vorkonfigurierte PubliiDB-Instanz

### Tests ausführen

```bash
# Alle Tests
uv run pytest

# Spezifischer Test
uv run pytest tests/test_db.py::TestPubliiDB::test_create_post

# Mit Verbose-Output
uv run pytest -v

# Mit Coverage
uv run pytest --cov=src/publii_mcp --cov-report=term-missing

# Nur schnelle Tests (exclude slow)
uv run pytest -m "not slow"
```

## Pull Request Guidelines

### Branch-Naming

```bash
# Feature
git checkout -b feature/add-image-upload

# Bugfix
git checkout -b fix/slug-generation-umlauts

# Documentation
git checkout -b docs/update-api-examples
```

### Commit Messages

Folge [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Dokumentation
- `style`: Formatierung (keine Code-Änderung)
- `refactor`: Code-Refactoring
- `test`: Tests hinzufügen/ändern
- `chore`: Build/Tooling-Änderungen

**Beispiele:**
```bash
git commit -m "feat(db): add image upload support for posts"
git commit -m "fix(slug): handle umlauts correctly in slug generation"
git commit -m "docs(api): add examples for batch operations"
git commit -m "test(db): add tests for multi-site support"
```

### Pull Request Checklist

Vor dem Erstellen eines PRs:

- [ ] Code folgt den Style-Guidelines (`ruff check --fix .` && `ruff format .`)
- [ ] Alle Tests bestehen (`pytest`)
- [ ] Neue Features haben Tests
- [ ] Dokumentation ist aktualisiert (README, docs/api.md, etc.)
- [ ] CHANGELOG.md ist aktualisiert (falls zutreffend)
- [ ] Commit-Messages folgen Conventional Commits
- [ ] Branch ist auf dem neuesten Stand mit `main`

### PR-Template

```markdown
## Beschreibung
<!-- Kurze Beschreibung der Änderungen -->

## Motivation
<!-- Warum ist diese Änderung notwendig? -->

## Typ
- [ ] Bugfix
- [ ] Feature
- [ ] Breaking Change
- [ ] Dokumentation

## Wie wurde getestet?
<!-- Beschreibe, wie du die Änderungen getestet hast -->

## Screenshots (falls UI-Änderungen)
<!-- Optional: Screenshots für visuelle Änderungen -->

## Checklist
- [ ] Code folgt Style-Guidelines
- [ ] Tests bestehen
- [ ] Dokumentation aktualisiert
- [ ] CHANGELOG.md aktualisiert
```

## Dokumentation

### Dokumentations-Struktur

```
docs/
├── api.md              # Vollständige API-Referenz
├── development.md      # Development-Guide
├── troubleshooting.md  # Häufige Probleme
└── examples.md         # Erweiterte Beispiele
```

### Dokumentation aktualisieren

Bei API-Änderungen:

1. **docs/api.md:** Tool-Signatur und Beispiele aktualisieren
2. **README.md:** Quick-Start aktualisieren (falls betroffen)
3. **CLAUDE.md:** AI-Kontext aktualisieren (falls nötig)
4. **docs/examples.md:** Neue Beispiele hinzufügen

### Docstring-Format

```python
def method(param1: str, param2: int) -> dict:
    """Kurze Beschreibung in einem Satz.

    Längere Beschreibung falls nötig. Kann mehrere
    Absätze umfassen.

    Args:
        param1: Beschreibung von param1
        param2: Beschreibung von param2

    Returns:
        Dict mit folgenden Keys:
        - id: Item-ID
        - name: Item-Name

    Raises:
        ValueError: Wenn param2 negativ ist
        KeyError: Wenn Required-Key fehlt

    Example:
        >>> result = method("test", 42)
        >>> print(result["id"])
        123
    """
```

## Feature-Entwicklung

### Neues MCP-Tool hinzufügen

1. **Implementiere in `db.py`** (falls DB-Zugriff nötig):
```python
def new_method(self, param: str) -> dict:
    """Neue Methode für Feature."""
    # Implementation
```

2. **Expose via MCP in `server.py`**:
```python
@mcp.tool()
def new_tool(param: str) -> dict:
    """MCP Tool für Feature.

    Args:
        param: Beschreibung

    Returns:
        Result-Dict
    """
    return _db.new_method(param)
```

3. **Füge Tests hinzu** in `tests/test_db.py`:
```python
def test_new_method(self, db_instance):
    result = db_instance.new_method("test")
    assert result["key"] == expected_value
```

4. **Dokumentiere in `docs/api.md`**:
```markdown
### `new_tool`

Beschreibung des Tools.

**Parameter:**
- `param` (str): Beschreibung

**Returns:** Dict mit ...

**Example:**
\`\`\`json
{
  "param": "test"
}
\`\`\`
```

## Release-Prozess

### Version Bump

```bash
# 1. Update Version in allen Dateien
# - pyproject.toml
# - src/publii_mcp/__init__.py
# - .claude-plugin/plugin.json
# - README.md (Badge)

# 2. Update CHANGELOG.md

# 3. Commit und Tag
git add .
git commit -m "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

### Semantic Versioning

Wir folgen [SemVer](https://semver.org/):

- **MAJOR (X.0.0):** Breaking Changes (API-Änderungen)
- **MINOR (0.X.0):** Neue Features (abwärtskompatibel)
- **PATCH (0.0.X):** Bugfixes

## Code Review

### Als Reviewer

- Überprüfe Code-Qualität und Style
- Teste den PR lokal
- Gib konstruktives Feedback
- Approve nur wenn alle Checks bestehen

### Feedback erhalten

- Nimm Feedback konstruktiv auf
- Diskutiere bei Unklarheiten
- Update den PR basierend auf Feedback
- Markiere resolved Conversations

## Community

### Kommunikation

- **GitHub Issues:** Bug Reports, Feature Requests
- **GitHub Discussions:** Fragen, Ideen, Diskussionen
- **Pull Requests:** Code-Beiträge

### Code of Conduct

- Sei respektvoll und konstruktiv
- Hilf anderen Entwicklern
- Folge den Projektrichtlinien
- Keine Diskriminierung oder Harassment

## Hilfe bekommen

### Debugging

- Siehe [docs/troubleshooting.md](docs/troubleshooting.md)
- Nutze `logging` für Debug-Output
- Prüfe Publii-Datenbank mit `sqlite3`

### Fragen stellen

- **Bugs:** Öffne ein Issue mit Reproduktionsschritten
- **Features:** Diskutiere Ideen in GitHub Discussions
- **Allgemeine Fragen:** Siehe Dokumentation oder frage in Discussions

## Danke!

Vielen Dank für deinen Beitrag zu publii-mcp! 🙌

Jeder Beitrag zählt - ob Bug Report, Feature Request, Dokumentation oder Code.
