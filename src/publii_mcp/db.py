"""SQLite-Abstraktionsschicht fur Publii CMS."""

import sqlite3
from datetime import datetime
from pathlib import Path


class PubliiDB:
    """Datenbank-Operationen fur Publii CMS."""

    def __init__(
        self,
        data_dir: Path,
        default_site: str | None = None,
    ) -> None:
        """Initialisiert PubliiDB.

        Args:
            data_dir: Pfad zum Publii-Datenverzeichnis (enthalt sites/).
            default_site: Standard-Site fur alle Operationen.

        Raises:
            ValueError: Wenn data_dir nicht existiert.
        """
        if not data_dir.exists():
            raise ValueError(f"Publii-Verzeichnis nicht gefunden: {data_dir}")

        self.data_dir = data_dir
        self.default_site = default_site

    def _get_db_path(self, site: str | None = None) -> Path:
        """Gibt den Pfad zur SQLite-Datenbank einer Site zuruck.

        Args:
            site: Site-Name. Nutzt default_site wenn None.

        Returns:
            Pfad zur db.sqlite Datei.

        Raises:
            ValueError: Wenn keine Site angegeben und kein Default gesetzt.
            ValueError: Wenn Site nicht existiert.
        """
        site_name = site or self.default_site
        if not site_name:
            raise ValueError("Keine Site angegeben und kein Default gesetzt")

        db_path = self.data_dir / "sites" / site_name / "input" / "db.sqlite"
        if not db_path.exists():
            raise ValueError(f"Site nicht gefunden: {site_name}")

        return db_path

    def list_sites(self) -> list[dict]:
        """Listet alle verfugbaren Publii-Sites.

        Returns:
            Liste von Dicts mit name und has_db.
        """
        sites_dir = self.data_dir / "sites"
        if not sites_dir.exists():
            return []

        sites = []
        for site_path in sorted(sites_dir.iterdir()):
            if site_path.is_dir():
                db_exists = (site_path / "input" / "db.sqlite").exists()
                sites.append({
                    "name": site_path.name,
                    "has_db": db_exists,
                })

        return sites

    def list_posts(
        self,
        site: str | None = None,
        status: str = "all",
        limit: int = 20,
    ) -> list[dict]:
        """Listet Blog-Posts einer Site.

        Args:
            site: Site-Name. Nutzt default_site wenn None.
            status: Filter: "all", "published", "draft".
            limit: Maximale Anzahl Posts.

        Returns:
            Liste von Post-Dicts sortiert nach created_at (neueste zuerst).
        """
        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Posts (keine Pages) - Pages haben ",is-page" im Status
        query = "SELECT * FROM posts WHERE status NOT LIKE '%,is-page%'"
        params: list = []

        if status == "published":
            query += " AND status = 'published'"
        elif status == "draft":
            query += " AND status = 'draft'"

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_post_dict(row) for row in rows]

    def _row_to_post_dict(self, row: sqlite3.Row) -> dict:
        """Konvertiert DB-Row zu Post-Dict."""
        return {
            "id": row["id"],
            "title": row["title"],
            "slug": row["slug"],
            "status": row["status"],
            "author_id": int(row["authors"]) if row["authors"] else None,
            "created_at": self._ms_to_iso(row["created_at"]),
            "modified_at": self._ms_to_iso(row["modified_at"]),
        }

    @staticmethod
    def _ms_to_iso(ms: int | None) -> str | None:
        """Konvertiert Millisekunden-Timestamp zu ISO-String."""
        if ms is None:
            return None
        return datetime.fromtimestamp(ms / 1000).isoformat()

    def get_post(self, post_id: int, site: str | None = None) -> dict:
        """Holt einen Blog-Post mit allen Details.

        Args:
            post_id: ID des Posts.
            site: Site-Name.

        Returns:
            Post-Dict mit vollem Content.

        Raises:
            ValueError: Wenn Post nicht existiert.
        """
        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM posts WHERE id = ? AND status NOT LIKE '%,is-page%'",
            (post_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            raise ValueError(f"Post mit ID {post_id} nicht gefunden")

        return self._row_to_full_post_dict(row)

    def _row_to_full_post_dict(self, row: sqlite3.Row) -> dict:
        """Konvertiert DB-Row zu vollstandigem Post-Dict."""
        base = self._row_to_post_dict(row)
        base["content"] = row["text"]
        base["featured_image_id"] = row["featured_image_id"]
        base["template"] = row["template"]
        return base
