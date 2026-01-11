# publii-mcp

MCP Server für Publii CMS - ermöglicht CRUD-Operationen auf Publii-Sites via Model Context Protocol.

## Projekt-Befehle

```bash
# Server starten
publii-mcp serve --site <site-name>

# Sites auflisten
publii-mcp info

# Tests
pytest

# Lint & Format
ruff check --fix . && ruff format .
```

## MCP-Konfiguration für Claude Code

```json
{
  "mcpServers": {
    "publii": {
      "command": "publii-mcp",
      "args": ["serve", "--site", "meine-site"]
    }
  }
}
```

## Verfügbare MCP-Tools

- **Sites:** `list_sites`, `get_site_info`
- **Posts:** `list_posts`, `get_post`, `create_post`, `update_post`, `delete_post`
- **Pages:** `list_pages`, `get_page`, `create_page`, `update_page`, `delete_page`
- **Metadata:** `list_tags`, `list_authors`

## Architektur

- `cli.py` - Typer CLI (serve, info)
- `server.py` - FastMCP Server mit Tool-Definitionen
- `db.py` - SQLite-Abstraktion für Publii-Datenbank

## Hinweise

- Posts/Pages werden standardmäßig als `draft` erstellt
- Slugs werden automatisch generiert (inkl. Umlaut-Konvertierung)
- Multi-Site-Support über `--site` Parameter

@docs/api.md
