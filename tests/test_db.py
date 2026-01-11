"""Tests fur PubliiDB."""

import sqlite3
from pathlib import Path

import pytest


class TestPubliiDB:
    """Tests fur die PubliiDB Klasse."""

    @pytest.fixture
    def temp_publii_dir(self, tmp_path: Path) -> Path:
        """Erstellt temporares Publii-Verzeichnis mit Test-Site."""
        sites_dir = tmp_path / "sites" / "test-site" / "input"
        sites_dir.mkdir(parents=True)

        db_path = sites_dir / "db.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Publii Schema erstellen
        cursor.executescript('''
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                authors TEXT,
                slug TEXT,
                text TEXT,
                featured_image_id INTEGER,
                created_at DATETIME,
                modified_at DATETIME,
                status TEXT,
                template TEXT
            );

            CREATE TABLE posts_additional_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                key TEXT,
                value TEXT
            );

            CREATE TABLE posts_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                url TEXT,
                title TEXT,
                caption TEXT,
                additional_data TEXT
            );

            CREATE TABLE tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                slug TEXT,
                description TEXT,
                additional_data TEXT
            );

            CREATE TABLE posts_tags (
                tag_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                PRIMARY KEY (tag_id, post_id)
            );

            CREATE TABLE authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                username TEXT,
                password TEXT,
                config TEXT,
                additional_data TEXT
            );

            INSERT INTO authors (id, name, username) VALUES (1, 'Admin', 'admin');
        ''')
        conn.commit()
        conn.close()

        return tmp_path

    def test_publii_db_init_with_valid_path(self, temp_publii_dir: Path) -> None:
        """PubliiDB initialisiert mit gultigen Pfad."""
        from publii_mcp.db import PubliiDB

        db = PubliiDB(data_dir=temp_publii_dir, default_site="test-site")

        assert db.data_dir == temp_publii_dir
        assert db.default_site == "test-site"

    def test_publii_db_init_with_invalid_path(self, tmp_path: Path) -> None:
        """PubliiDB wirft Error bei ungultigem Pfad."""
        from publii_mcp.db import PubliiDB

        with pytest.raises(ValueError, match="nicht gefunden"):
            PubliiDB(data_dir=tmp_path / "nonexistent", default_site="test")

    def test_list_sites_returns_available_sites(self, temp_publii_dir: Path) -> None:
        """list_sites gibt alle Sites mit DB zuruck."""
        from publii_mcp.db import PubliiDB

        # Zweite Site erstellen
        site2_dir = temp_publii_dir / "sites" / "second-site" / "input"
        site2_dir.mkdir(parents=True)
        conn = sqlite3.connect(site2_dir / "db.sqlite")
        conn.execute("CREATE TABLE posts (id INTEGER)")
        conn.close()

        db = PubliiDB(data_dir=temp_publii_dir)
        sites = db.list_sites()

        assert len(sites) == 2
        assert {"name": "second-site", "has_db": True} in sites
        assert {"name": "test-site", "has_db": True} in sites

    def test_list_sites_marks_sites_without_db(self, temp_publii_dir: Path) -> None:
        """list_sites markiert Sites ohne DB."""
        from publii_mcp.db import PubliiDB

        # Site ohne DB erstellen
        (temp_publii_dir / "sites" / "no-db-site" / "input").mkdir(parents=True)

        db = PubliiDB(data_dir=temp_publii_dir)
        sites = db.list_sites()

        no_db_site = next(s for s in sites if s["name"] == "no-db-site")
        assert no_db_site["has_db"] is False
