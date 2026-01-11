"""FastMCP Server fur Publii CMS."""

from pathlib import Path

from fastmcp import FastMCP

from publii_mcp.db import PubliiDB

# Globale Variable fur DB-Instanz (wird bei Server-Start gesetzt)
_db: PubliiDB | None = None


def create_server(
    data_dir: Path,
    default_site: str | None = None,
) -> FastMCP:
    """Erstellt und konfiguriert den FastMCP Server.

    Args:
        data_dir: Pfad zum Publii-Datenverzeichnis.
        default_site: Standard-Site fur alle Operationen.

    Returns:
        Konfigurierter FastMCP Server.
    """
    global _db
    _db = PubliiDB(data_dir=data_dir, default_site=default_site)

    mcp = FastMCP("publii-mcp")

    # === Sites ===

    @mcp.tool
    def list_sites() -> list[dict]:
        """Listet alle verfugbaren Publii-Sites."""
        return _db.list_sites()

    @mcp.tool
    def get_site_info(site: str | None = None) -> dict:
        """Zeigt Details einer Site."""
        sites = _db.list_sites()
        site_name = site or _db.default_site

        for s in sites:
            if s["name"] == site_name:
                return s

        return {"error": f"Site nicht gefunden: {site_name}"}

    # === Posts ===

    @mcp.tool
    def list_posts(
        site: str | None = None,
        status: str = "all",
        limit: int = 20,
    ) -> list[dict]:
        """Listet Blog-Posts einer Site.

        Args:
            site: Site-Name (nutzt Default wenn leer).
            status: Filter: all, published, draft.
            limit: Maximale Anzahl Posts.
        """
        return _db.list_posts(site=site, status=status, limit=limit)

    @mcp.tool
    def get_post(post_id: int, site: str | None = None) -> dict:
        """Holt einen Blog-Post mit allen Details."""
        return _db.get_post(post_id=post_id, site=site)

    @mcp.tool
    def create_post(
        title: str,
        content: str,
        site: str | None = None,
        slug: str | None = None,
        status: str = "draft",
        author_id: int = 1,
    ) -> dict:
        """Erstellt einen neuen Blog-Post.

        Args:
            title: Post-Titel.
            content: HTML-Inhalt.
            site: Site-Name.
            slug: URL-Slug (auto-generiert wenn leer).
            status: draft oder published.
            author_id: ID des Autors.
        """
        return _db.create_post(
            title=title,
            content=content,
            site=site,
            slug=slug,
            status=status,
            author_id=author_id,
        )

    @mcp.tool
    def update_post(
        post_id: int,
        site: str | None = None,
        title: str | None = None,
        content: str | None = None,
        status: str | None = None,
    ) -> dict:
        """Aktualisiert einen Blog-Post."""
        return _db.update_post(
            post_id=post_id,
            site=site,
            title=title,
            content=content,
            status=status,
        )

    @mcp.tool
    def delete_post(post_id: int, site: str | None = None) -> dict:
        """Loscht einen Blog-Post."""
        return _db.delete_post(post_id=post_id, site=site)

    # === Pages ===

    @mcp.tool
    def list_pages(
        site: str | None = None,
        status: str = "all",
        limit: int = 20,
    ) -> list[dict]:
        """Listet statische Seiten einer Site."""
        return _db.list_pages(site=site, status=status, limit=limit)

    @mcp.tool
    def get_page(page_id: int, site: str | None = None) -> dict:
        """Holt eine statische Seite mit allen Details."""
        return _db.get_page(page_id=page_id, site=site)

    @mcp.tool
    def create_page(
        title: str,
        content: str,
        site: str | None = None,
        slug: str | None = None,
        status: str = "draft",
        author_id: int = 1,
    ) -> dict:
        """Erstellt eine neue statische Seite."""
        return _db.create_page(
            title=title,
            content=content,
            site=site,
            slug=slug,
            status=status,
            author_id=author_id,
        )

    @mcp.tool
    def update_page(
        page_id: int,
        site: str | None = None,
        title: str | None = None,
        content: str | None = None,
        status: str | None = None,
    ) -> dict:
        """Aktualisiert eine statische Seite."""
        return _db.update_page(
            page_id=page_id,
            site=site,
            title=title,
            content=content,
            status=status,
        )

    @mcp.tool
    def delete_page(page_id: int, site: str | None = None) -> dict:
        """Loscht eine statische Seite."""
        return _db.delete_page(page_id=page_id, site=site)

    # === Tags & Authors ===

    @mcp.tool
    def list_tags(site: str | None = None) -> list[dict]:
        """Listet alle Tags einer Site."""
        return _db.list_tags(site=site)

    @mcp.tool
    def list_authors(site: str | None = None) -> list[dict]:
        """Listet alle Autoren einer Site."""
        return _db.list_authors(site=site)

    return mcp
