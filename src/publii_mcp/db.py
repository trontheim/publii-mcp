"""SQLite-Abstraktionsschicht fur Publii CMS."""

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
