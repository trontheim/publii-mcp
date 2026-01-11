"""SQLite-Abstraktionsschicht fur Publii CMS."""

import json
import re
import sqlite3
import time
import unicodedata
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

    @staticmethod
    def _generate_slug(title: str) -> str:
        """Generiert URL-freundlichen Slug aus Titel.

        Umlaute werden konvertiert (a -> ae, etc.),
        Sonderzeichen entfernt, Leerzeichen zu Bindestrichen.
        """
        # Umlaute konvertieren
        umlaut_map = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
            'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
            'ß': 'ss',
        }
        slug = title
        for umlaut, replacement in umlaut_map.items():
            slug = slug.replace(umlaut, replacement)

        # Auf ASCII normalisieren
        slug = unicodedata.normalize('NFKD', slug)
        slug = slug.encode('ascii', 'ignore').decode('ascii')

        # Nur alphanumerisch und Leerzeichen behalten
        slug = re.sub(r'[^\w\s-]', '', slug.lower())

        # Leerzeichen zu Bindestrichen
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')

        return slug

    def validate_author_exists(self, author_id: int, site: str | None = None) -> bool:
        """Pruft ob Author existiert."""
        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM authors WHERE id = ?", (author_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def _create_additional_data(
        self,
        post_id: int,
        is_page: bool = False,
        site: str | None = None,
    ) -> None:
        """Erstellt _core und postViewSettings/pageViewSettings Eintrage."""
        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # _core Eintrag
        core_data = {
            "metaTitle": "",
            "metaDesc": "",
            "metaRobots": "index, follow",
            "canonicalUrl": "",
            "editor": "tinymce",
            "mainTag": "",
        }
        cursor.execute(
            "INSERT INTO posts_additional_data (post_id, key, value) VALUES (?, ?, ?)",
            (post_id, "_core", json.dumps(core_data))
        )

        # View Settings
        if is_page:
            view_settings = {
                "displayDate": {"type": "select"},
                "displayAuthor": {"type": "select"},
                "displayLastUpdatedDate": {"type": "select"},
                "displayShareButtons": {"type": "select"},
                "displayAuthorBio": {"type": "select"},
                "displayChildPages": {"type": "select"},
                "displayComments": {"type": "select"},
            }
            key = "pageViewSettings"
        else:
            view_settings = {
                "displayDate": {"type": "select"},
                "displayAuthor": {"type": "select"},
                "displayLastUpdatedDate": {"type": "select"},
                "displayTags": {"type": "select"},
                "displayShareButtons": {"type": "select"},
                "displayAuthorBio": {"type": "select"},
                "displayPostNavigation": {"type": "select"},
                "displayRelatedPosts": {"type": "select"},
                "displayComments": {"type": "select"},
            }
            key = "postViewSettings"

        cursor.execute(
            "INSERT INTO posts_additional_data (post_id, key, value) VALUES (?, ?, ?)",
            (post_id, key, json.dumps(view_settings))
        )

        conn.commit()
        conn.close()

    def create_post(
        self,
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
            slug: URL-Slug (auto-generiert wenn None).
            status: "draft" oder "published".
            author_id: ID des Autors.

        Returns:
            Dict mit erstelltem Post.

        Raises:
            ValueError: Bei ungultigem author_id oder status.
        """
        # Validierung
        if not self.validate_author_exists(author_id, site):
            raise ValueError(f"Author mit ID {author_id} nicht gefunden")

        if status not in ("draft", "published"):
            raise ValueError(f"Ungultiger Status: {status}")

        # Slug generieren
        post_slug = slug or self._generate_slug(title)

        # Timestamp in Millisekunden
        now_ms = int(time.time() * 1000)

        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO posts (title, authors, slug, text, status, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, str(author_id), post_slug, content, status, now_ms, now_ms)
        )
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Additional Data erstellen
        self._create_additional_data(post_id, is_page=False, site=site)

        return {
            "id": post_id,
            "title": title,
            "slug": post_slug,
            "status": status,
            "author_id": author_id,
            "created_at": self._ms_to_iso(now_ms),
        }

    def update_post(
        self,
        post_id: int,
        site: str | None = None,
        title: str | None = None,
        content: str | None = None,
        status: str | None = None,
    ) -> dict:
        """Aktualisiert einen Blog-Post.

        Args:
            post_id: ID des Posts.
            site: Site-Name.
            title: Neuer Titel (optional).
            content: Neuer HTML-Inhalt (optional).
            status: Neuer Status (optional).

        Returns:
            Aktualisierter Post.

        Raises:
            ValueError: Wenn Post nicht existiert.
        """
        # Prufung ob Post existiert
        self.get_post(post_id, site)  # Wirft ValueError wenn nicht gefunden

        if status is not None and status not in ("draft", "published"):
            raise ValueError(f"Ungultiger Status: {status}")

        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if content is not None:
            updates.append("text = ?")
            params.append(content)

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if updates:
            updates.append("modified_at = ?")
            params.append(int(time.time() * 1000))
            params.append(post_id)

            cursor.execute(
                f"UPDATE posts SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()

        conn.close()

        return self.get_post(post_id, site)

    def delete_post(self, post_id: int, site: str | None = None) -> dict:
        """Loscht einen Blog-Post inkl. zugehoriger Daten.

        Args:
            post_id: ID des Posts.
            site: Site-Name.

        Returns:
            Dict mit Bestatigung.

        Raises:
            ValueError: Wenn Post nicht existiert.
        """
        # Prufung ob Post existiert
        post = self.get_post(post_id, site)

        db_path = self._get_db_path(site)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Zugehorige Daten loschen
        cursor.execute("DELETE FROM posts_additional_data WHERE post_id = ?", (post_id,))
        cursor.execute("DELETE FROM posts_images WHERE post_id = ?", (post_id,))
        cursor.execute("DELETE FROM posts_tags WHERE post_id = ?", (post_id,))

        # Post loschen
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))

        conn.commit()
        conn.close()

        return {"deleted": True, "id": post_id, "title": post["title"]}
