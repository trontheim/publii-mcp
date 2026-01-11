# Troubleshooting

Häufige Probleme und Lösungen für publii-mcp.

## Installation

### Problem: `publii-mcp` Befehl nicht gefunden

**Lösung:**
```bash
# Stelle sicher, dass uv tool install korrekt ausgeführt wurde
uv tool install .

# Überprüfe, ob der Befehl verfügbar ist
which publii-mcp

# Falls nicht gefunden, füge uv tools zum PATH hinzu
export PATH="$HOME/.local/bin:$PATH"
```

### Problem: Python-Version zu alt

**Fehler:** `requires-python = ">=3.10"`

**Lösung:**
```bash
# Installiere Python 3.10+ mit asdf
asdf install python 3.13.3
asdf global python 3.13.3

# Oder mit uv
uv python install 3.13
```

## MCP Server

### Problem: Site nicht gefunden

**Fehler:** `ValueError: Site nicht gefunden: meine-site`

**Ursachen:**
1. Site existiert nicht unter `~/Documents/Publii/sites/`
2. Tippfehler im Site-Namen
3. Falsches Data-Directory

**Lösung:**
```bash
# Liste verfügbare Sites auf
publii-mcp info

# Verwende exakten Site-Namen (case-sensitive)
publii-mcp serve --site "Meine-Site"

# Oder gib custom Data-Directory an
publii-mcp serve --data-dir /pfad/zu/publii
```

### Problem: Datenbank-Fehler

**Fehler:** `sqlite3.OperationalError: unable to open database file`

**Ursachen:**
1. Keine Lese-/Schreibrechte
2. Datenbank beschädigt
3. Publii nutzt die Datenbank gerade

**Lösung:**
```bash
# Überprüfe Berechtigungen
ls -la ~/Documents/Publii/sites/meine-site/input/

# Schließe Publii vor MCP-Operationen
# Publii und MCP sollten nicht gleichzeitig auf die DB zugreifen

# Bei Beschädigung: Backup verwenden
cp ~/Documents/Publii/sites/meine-site/input/db.sqlite.backup \
   ~/Documents/Publii/sites/meine-site/input/db.sqlite
```

## Claude Code Plugin

### Problem: Plugin wird nicht erkannt

**Lösung:**
```bash
# Stelle sicher, dass .claude-plugin/plugin.json existiert
cat .claude-plugin/plugin.json

# Reinstalliere das Plugin
cd /pfad/zu/publii-mcp
uv tool install .

# Starte Claude Code neu
```

### Problem: MCP Server startet nicht

**Fehler in Claude Code Logs:** `Command failed: uv run publii-mcp serve`

**Lösung:**
```bash
# Teste manuell
cd /pfad/zu/publii-mcp
uv run publii-mcp serve

# Überprüfe .mcp.json Konfiguration
cat .mcp.json

# Stelle sicher, dass uv im PATH ist
which uv
```

## Posts & Pages

### Problem: Post wird nicht erstellt

**Fehler:** `ValueError: Autor mit ID X nicht gefunden`

**Lösung:**
```bash
# Liste verfügbare Autoren auf
# Verwende MCP Tool: list_authors

# Erstelle Post mit gültigem author_id
# Standard-Autor ist meist ID 1
```

### Problem: Slug-Kollision

**Fehler:** `UNIQUE constraint failed: posts.slug`

**Ursachen:**
- Post/Page mit gleichem Slug existiert bereits
- Automatische Slug-Generierung erzeugt Duplikat

**Lösung:**
```python
# Gib expliziten Slug an
create_post(
    title="Mein Titel",
    slug="mein-titel-v2",  # Custom slug
    ...
)

# Oder ändere den Titel leicht
create_post(
    title="Mein Titel (neu)",  # → slug: mein-titel-neu
    ...
)
```

### Problem: Umlaute im Slug

**Erwartetes Verhalten:** Umlaute werden automatisch konvertiert:
- `ä` → `ae`
- `ö` → `oe`
- `ü` → `ue`
- `ß` → `ss`

**Beispiel:**
```python
create_post(title="Über Äpfel und Öl")
# Generierter Slug: "ueber-aepfel-und-oel"
```

## Development

### Problem: Tests schlagen fehl

**Lösung:**
```bash
# Installiere Dev-Dependencies
uv sync --all-groups

# Führe Tests mit Details aus
pytest -v

# Mit Coverage
pytest --cov=src/publii_mcp --cov-report=term-missing
```

### Problem: Ruff-Fehler

**Lösung:**
```bash
# Auto-Fix für Linting-Probleme
ruff check --fix .

# Formatiere Code
ruff format .

# Zeige Regeln an
ruff rule E501  # Beispiel: line too long
```

## Debugging

### Debug-Modus aktivieren

Füge Logging in `cli.py` oder `server.py` hinzu:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In Funktionen
logger.debug(f"Site: {site}, Status: {status}")
```

### Datenbank-Inspektion

```bash
# Öffne Datenbank mit sqlite3
sqlite3 ~/Documents/Publii/sites/meine-site/input/db.sqlite

# Nützliche Queries
.tables                              # Zeige Tabellen
.schema posts                        # Zeige Schema
SELECT id, title, slug FROM posts;   # Liste Posts
SELECT * FROM authors;               # Liste Autoren
.quit                                # Beenden
```

### MCP-Logs prüfen

Claude Code speichert MCP-Logs unter:
```
~/.claude/logs/mcp/
```

Überprüfe die Logs für detaillierte Fehlermeldungen.

## Bekannte Limitationen

1. **Gleichzeitiger Zugriff:** Publii und MCP sollten nicht gleichzeitig auf dieselbe Datenbank zugreifen
2. **Images:** MCP unterstützt derzeit keine Bild-Uploads (manuelle Uploads via Publii erforderlich)
3. **Rich Content:** Komplexe Editor-Blöcke müssen manuell als HTML/JSON formatiert werden
4. **Multi-Site:** Nur ein Site kann pro MCP-Server-Instanz aktiv sein

## Weiterführende Hilfe

- **GitHub Issues:** [github.com/trontheim/publii-mcp/issues](https://github.com/trontheim/publii-mcp/issues)
- **API-Dokumentation:** [docs/api.md](api.md)
- **Development Guide:** [docs/development.md](development.md)
