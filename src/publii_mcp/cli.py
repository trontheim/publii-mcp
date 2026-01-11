"""Typer CLI fur publii-mcp Server."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="publii-mcp",
    help="MCP Server fur Publii CMS",
    no_args_is_help=True,
)
console = Console()

DEFAULT_DATA_DIR = Path.home() / "Documents" / "Publii"


@app.command()
def serve(
    site: str | None = typer.Option(
        None,
        "--site",
        "-s",
        help="Default-Site fur alle Operationen",
    ),
    data_dir: Path = typer.Option(
        DEFAULT_DATA_DIR,
        "--data-dir",
        "-d",
        help="Publii Daten-Verzeichnis",
    ),
) -> None:
    """Startet den MCP Server (stdio)."""
    from publii_mcp.server import create_server

    if not data_dir.exists():
        console.print(f"[red]Fehler: Verzeichnis nicht gefunden: {data_dir}[/red]")
        raise typer.Exit(1)

    server = create_server(data_dir=data_dir, default_site=site)
    server.run()


@app.command()
def info(
    data_dir: Path = typer.Option(
        DEFAULT_DATA_DIR,
        "--data-dir",
        "-d",
        help="Publii Daten-Verzeichnis",
    ),
) -> None:
    """Zeigt Informationen uber verfugbare Sites."""
    sites_dir = data_dir / "sites"

    if not sites_dir.exists():
        console.print(f"[red]Verzeichnis nicht gefunden: {sites_dir}[/red]")
        raise typer.Exit(1)

    table = Table(title="Verfugbare Publii Sites")
    table.add_column("Site", style="cyan")
    table.add_column("DB vorhanden", style="green")

    for site_path in sorted(sites_dir.iterdir()):
        if site_path.is_dir():
            db_exists = (site_path / "input" / "db.sqlite").exists()
            table.add_row(site_path.name, "✓" if db_exists else "✗")

    console.print(table)


if __name__ == "__main__":
    app()
