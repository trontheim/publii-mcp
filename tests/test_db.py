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

    @pytest.fixture
    def db_with_posts(self, temp_publii_dir: Path) -> "PubliiDB":
        """PubliiDB mit Test-Posts."""
        from publii_mcp.db import PubliiDB

        db_path = temp_publii_dir / "sites" / "test-site" / "input" / "db.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test-Posts einfugen (Timestamp in Millisekunden!)
        cursor.executescript('''
            INSERT INTO posts (id, title, authors, slug, text, status, created_at, modified_at)
            VALUES
                (1, 'Erster Post', '1', 'erster-post', '<p>Inhalt 1</p>', 'published', 1704067200000, 1704067200000),
                (2, 'Zweiter Post', '1', 'zweiter-post', '<p>Inhalt 2</p>', 'draft', 1704153600000, 1704153600000),
                (3, 'Eine Seite', '1', 'eine-seite', '<p>Seite</p>', 'published,is-page', 1704240000000, 1704240000000);
        ''')
        conn.commit()
        conn.close()

        return PubliiDB(data_dir=temp_publii_dir, default_site="test-site")

    def test_list_posts_returns_all_posts(self, db_with_posts) -> None:
        """list_posts gibt alle Posts (keine Pages) zuruck."""
        posts = db_with_posts.list_posts()

        assert len(posts) == 2
        assert posts[0]["title"] == "Zweiter Post"  # Neuester zuerst
        assert posts[1]["title"] == "Erster Post"

    def test_list_posts_filters_by_status(self, db_with_posts) -> None:
        """list_posts filtert nach Status."""
        published = db_with_posts.list_posts(status="published")
        drafts = db_with_posts.list_posts(status="draft")

        assert len(published) == 1
        assert published[0]["title"] == "Erster Post"
        assert len(drafts) == 1
        assert drafts[0]["title"] == "Zweiter Post"

    def test_list_posts_respects_limit(self, db_with_posts) -> None:
        """list_posts beachtet Limit."""
        posts = db_with_posts.list_posts(limit=1)

        assert len(posts) == 1

    def test_get_post_returns_full_post(self, db_with_posts) -> None:
        """get_post gibt vollstandigen Post mit Content zuruck."""
        post = db_with_posts.get_post(1)

        assert post["id"] == 1
        assert post["title"] == "Erster Post"
        assert post["content"] == "<p>Inhalt 1</p>"
        assert post["slug"] == "erster-post"

    def test_get_post_raises_for_nonexistent(self, db_with_posts) -> None:
        """get_post wirft Error fur nicht existierenden Post."""
        with pytest.raises(ValueError, match="Post mit ID 999 nicht gefunden"):
            db_with_posts.get_post(999)

    def test_create_post_creates_new_post(self, db_with_posts) -> None:
        """create_post erstellt neuen Post."""
        result = db_with_posts.create_post(
            title="Neuer Post",
            content="<p>Neuer Inhalt</p>",
        )

        assert result["id"] == 4  # Nach den 3 Test-Posts
        assert result["title"] == "Neuer Post"
        assert result["status"] == "draft"
        assert result["slug"] == "neuer-post"

    def test_create_post_generates_slug(self, db_with_posts) -> None:
        """create_post generiert Slug aus Titel."""
        result = db_with_posts.create_post(
            title="Mein Toller Artikel!",
            content="<p>Test</p>",
        )

        assert result["slug"] == "mein-toller-artikel"

    def test_create_post_validates_author(self, db_with_posts) -> None:
        """create_post validiert Author-ID."""
        with pytest.raises(ValueError, match="Author mit ID 999 nicht gefunden"):
            db_with_posts.create_post(
                title="Test",
                content="<p>Test</p>",
                author_id=999,
            )

    def test_create_post_creates_additional_data(self, db_with_posts) -> None:
        """create_post erstellt posts_additional_data Eintrage."""
        result = db_with_posts.create_post(
            title="Test Post",
            content="<p>Test</p>",
        )

        # Prufen ob _core und postViewSettings erstellt wurden
        db_path = db_with_posts._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key FROM posts_additional_data WHERE post_id = ?",
            (result["id"],)
        )
        keys = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "_core" in keys
        assert "postViewSettings" in keys

    def test_update_post_updates_fields(self, db_with_posts) -> None:
        """update_post aktualisiert angegebene Felder."""
        result = db_with_posts.update_post(
            post_id=1,
            title="Aktualisierter Titel",
        )

        assert result["title"] == "Aktualisierter Titel"
        # Slug bleibt unverandert
        assert result["slug"] == "erster-post"

    def test_update_post_raises_for_nonexistent(self, db_with_posts) -> None:
        """update_post wirft Error fur nicht existierenden Post."""
        with pytest.raises(ValueError, match="Post mit ID 999 nicht gefunden"):
            db_with_posts.update_post(post_id=999, title="Test")

    def test_delete_post_removes_post(self, db_with_posts) -> None:
        """delete_post loscht Post und zugehorige Daten."""
        db_with_posts.delete_post(1)

        with pytest.raises(ValueError):
            db_with_posts.get_post(1)

    def test_delete_post_removes_related_data(self, db_with_posts) -> None:
        """delete_post loscht auch posts_additional_data."""
        # Erst Post mit additional_data erstellen
        result = db_with_posts.create_post(title="Temp", content="<p>Temp</p>")
        post_id = result["id"]

        # Loschen
        db_with_posts.delete_post(post_id)

        # Prufen dass additional_data geloscht wurde
        db_path = db_with_posts._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM posts_additional_data WHERE post_id = ?",
            (post_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0


class TestPubliiDBPages:
    """Tests fur Page-Operationen."""

    @pytest.fixture
    def temp_publii_dir(self, tmp_path: Path) -> Path:
        """Erstellt temporares Publii-Verzeichnis mit Test-Site."""
        sites_dir = tmp_path / "sites" / "test-site" / "input"
        sites_dir.mkdir(parents=True)

        db_path = sites_dir / "db.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.executescript('''
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, authors TEXT, slug TEXT, text TEXT,
                featured_image_id INTEGER, created_at DATETIME,
                modified_at DATETIME, status TEXT, template TEXT
            );
            CREATE TABLE posts_additional_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER, key TEXT, value TEXT
            );
            CREATE TABLE posts_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER, url TEXT, title TEXT, caption TEXT, additional_data TEXT
            );
            CREATE TABLE tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, slug TEXT, description TEXT, additional_data TEXT
            );
            CREATE TABLE posts_tags (tag_id INTEGER, post_id INTEGER, PRIMARY KEY (tag_id, post_id));
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, username TEXT, password TEXT, config TEXT, additional_data TEXT
            );
            INSERT INTO authors (id, name, username) VALUES (1, 'Admin', 'admin');
        ''')
        conn.commit()
        conn.close()

        return tmp_path

    @pytest.fixture
    def db_with_pages(self, temp_publii_dir: Path) -> "PubliiDB":
        """PubliiDB mit Test-Pages."""
        from publii_mcp.db import PubliiDB

        db_path = temp_publii_dir / "sites" / "test-site" / "input" / "db.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.executescript('''
            INSERT INTO posts (id, title, authors, slug, text, status, created_at, modified_at)
            VALUES
                (10, 'Uber uns', '1', 'ueber-uns', '<p>Uber uns</p>', 'published,is-page', 1704067200000, 1704067200000),
                (11, 'Impressum', '1', 'impressum', '<p>Impressum</p>', 'draft,is-page', 1704153600000, 1704153600000);
        ''')
        conn.commit()
        conn.close()

        return PubliiDB(data_dir=temp_publii_dir, default_site="test-site")

    def test_list_pages_returns_only_pages(self, db_with_pages) -> None:
        """list_pages gibt nur Pages zuruck."""
        pages = db_with_pages.list_pages()

        assert len(pages) == 2
        assert all("is-page" in p.get("status", "") or p.get("is_page") for p in pages)

    def test_get_page_returns_page(self, db_with_pages) -> None:
        """get_page gibt Page mit Content zuruck."""
        page = db_with_pages.get_page(10)

        assert page["title"] == "Uber uns"
        assert page["content"] == "<p>Uber uns</p>"

    def test_create_page_adds_is_page_suffix(self, db_with_pages) -> None:
        """create_page fugt ,is-page zum Status hinzu."""
        result = db_with_pages.create_page(
            title="Kontakt",
            content="<p>Kontakt</p>",
        )

        assert ",is-page" in result["status"]
