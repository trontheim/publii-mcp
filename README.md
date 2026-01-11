# publii-mcp

MCP Server fur Publii CMS. Ermoglicht Claude Code und anderen MCP-Clients die Interaktion mit Publii-Websites.

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

# Verfugbare Sites anzeigen
publii-mcp info
```

## Features

- 16 MCP Tools fur Posts, Pages, Tags, Authors, Images
- Multi-Site Support
- Draft-first Workflow
- Automatische Slug-Generierung
