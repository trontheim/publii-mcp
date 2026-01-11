# Erweiterte Beispiele

Praktische Anwendungsbeispiele für publii-mcp.

## Beispiel 1: Blog-Migration von WordPress

Migriere Posts von WordPress zu Publii mit Python-Script:

```python
from publii_mcp.db import PubliiDB
import json

# WordPress-Export (JSON)
with open("wordpress_export.json") as f:
    wp_posts = json.load(f)

# Publii-Datenbank initialisieren
db = PubliiDB(site="my-blog")

# Migriere Posts
for wp_post in wp_posts:
    publii_post = db.create_post(
        title=wp_post["title"],
        text=wp_post["content"],
        author_id=1,
        status="draft",  # Erst als Draft, später veröffentlichen
        created_at=wp_post["date"],  # ISO-String oder Millisekunden
    )
    print(f"✓ Migriert: {publii_post['title']} (ID: {publii_post['id']})")
```

## Beispiel 2: Bulk-Tagging

Füge Tags zu mehreren Posts hinzu:

```python
from publii_mcp.db import PubliiDB

db = PubliiDB(site="tech-blog")

# Liste alle Posts mit "Python" im Titel
posts = db.list_posts(limit=100)
python_posts = [p for p in posts if "Python" in p["title"]]

# Tag-IDs ermitteln
tags = db.list_tags()
python_tag_id = next(t["id"] for t in tags if t["name"] == "Python")

# Füge Tag zu allen Posts hinzu
for post in python_posts:
    db.update_post(
        post_id=post["id"],
        tag_ids=[python_tag_id],  # Bestehende Tags werden überschrieben!
    )
    print(f"✓ Tagged: {post['title']}")
```

**Warnung:** `tag_ids` überschreibt bestehende Tags. Für Append-Verhalten:

```python
# Bestehende Tags beibehalten
post_full = db.get_post(post["id"])
existing_tag_ids = post_full.get("tag_ids", [])
new_tag_ids = list(set(existing_tag_ids + [python_tag_id]))

db.update_post(post_id=post["id"], tag_ids=new_tag_ids)
```

## Beispiel 3: Automatische Post-Generierung

Erstelle Posts aus CSV-Datei:

```python
import csv
from publii_mcp.db import PubliiDB

db = PubliiDB(site="product-catalog")

with open("products.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        post = db.create_post(
            title=row["product_name"],
            text=f"""
            <h2>Beschreibung</h2>
            <p>{row["description"]}</p>

            <h2>Preis</h2>
            <p>{row["price"]} EUR</p>

            <h2>Verfügbarkeit</h2>
            <p>{row["stock"]} Stück auf Lager</p>
            """,
            slug=row["sku"].lower(),  # SKU als Slug
            author_id=1,
            status="draft",
        )
        print(f"✓ Erstellt: {post['title']}")
```

## Beispiel 4: Draft-Review-Workflow

Automatischer Workflow für Draft-Review:

```python
from publii_mcp.db import PubliiDB
from datetime import datetime, timedelta

db = PubliiDB(site="my-blog")

# Finde alle Drafts älter als 7 Tage
drafts = db.list_posts(status="draft", limit=100)
seven_days_ago = datetime.now() - timedelta(days=7)

old_drafts = [
    d for d in drafts
    if datetime.fromisoformat(d["created_at"]) < seven_days_ago
]

print(f"\n📋 {len(old_drafts)} alte Drafts gefunden:\n")

for draft in old_drafts:
    age_days = (datetime.now() - datetime.fromisoformat(draft["created_at"])).days
    print(f"- {draft['title']} ({age_days} Tage alt)")
    print(f"  Slug: {draft['slug']}")
    print(f"  ID: {draft['id']}\n")

# Optional: Batch-Veröffentlichung
# for draft in old_drafts:
#     db.update_post(post_id=draft["id"], status="published")
```

## Beispiel 5: Multi-Site-Management

Verwalte mehrere Publii-Sites:

```python
from publii_mcp.db import PubliiDB

sites = ["blog-de", "blog-en", "blog-fr"]

for site_name in sites:
    db = PubliiDB(site=site_name)

    # Erstelle "About"-Page für jede Site
    about_pages = {
        "blog-de": ("Über uns", "Willkommen auf unserem deutschen Blog..."),
        "blog-en": ("About Us", "Welcome to our English blog..."),
        "blog-fr": ("À propos", "Bienvenue sur notre blog français..."),
    }

    title, content = about_pages[site_name]
    page = db.create_page(
        title=title,
        text=f"<p>{content}</p>",
        author_id=1,
        status="published",
    )

    print(f"✓ {site_name}: {page['title']} erstellt")
```

## Beispiel 6: Content-Audit

Analysiere Content-Metriken:

```python
from publii_mcp.db import PubliiDB
from collections import Counter

db = PubliiDB(site="analytics-blog")

# Lade alle Posts
posts = db.list_posts(status="all", limit=500)
tags = db.list_tags()
authors = db.list_authors()

# Tag-Verwendung
tag_usage = Counter()
for post in posts:
    post_full = db.get_post(post["id"])
    for tag_id in post_full.get("tag_ids", []):
        tag_name = next(t["name"] for t in tags if t["id"] == tag_id)
        tag_usage[tag_name] += 1

# Autor-Statistiken
author_stats = Counter()
for post in posts:
    author_name = next(a["name"] for a in authors if a["id"] == post["author_id"])
    author_stats[author_name] += 1

# Report
print("📊 Content-Audit\n")
print(f"Gesamt-Posts: {len(posts)}")
print(f"Gesamt-Tags: {len(tags)}")
print(f"Gesamt-Autoren: {len(authors)}\n")

print("Top 10 Tags:")
for tag, count in tag_usage.most_common(10):
    print(f"  {tag}: {count} Posts")

print("\nPosts pro Autor:")
for author, count in author_stats.most_common():
    print(f"  {author}: {count} Posts")
```

## Beispiel 7: Scheduled Publishing (Cron)

Automatisches Veröffentlichen geplanter Posts:

```python
#!/usr/bin/env python3
"""
Speichere als: ~/.local/bin/publii-publish-scheduled
Cron: 0 * * * * ~/.local/bin/publii-publish-scheduled
"""

from publii_mcp.db import PubliiDB
from datetime import datetime
import time

db = PubliiDB(site="scheduled-blog")

# Finde Drafts mit "publish_date" im Text (Custom Field)
drafts = db.list_posts(status="draft", limit=100)
now = datetime.now()

for draft in drafts:
    full_post = db.get_post(draft["id"])
    text = full_post.get("text", "")

    # Suche nach: <!-- publish_date: 2024-01-15T10:00:00 -->
    if "<!-- publish_date:" in text:
        date_str = text.split("<!-- publish_date:")[1].split("-->")[0].strip()
        publish_date = datetime.fromisoformat(date_str)

        if publish_date <= now:
            db.update_post(
                post_id=draft["id"],
                status="published",
                text=text.replace(f"<!-- publish_date: {date_str} -->", ""),
            )
            print(f"✓ Veröffentlicht: {draft['title']}")
```

**Cron Setup:**
```bash
chmod +x ~/.local/bin/publii-publish-scheduled
crontab -e
# Füge hinzu: 0 * * * * ~/.local/bin/publii-publish-scheduled
```

## Beispiel 8: Backup-Script

Automatisches Backup der Publii-Datenbank:

```bash
#!/bin/bash
# Speichere als: ~/bin/publii-backup.sh

SITE="my-blog"
DB_PATH="$HOME/Documents/Publii/sites/$SITE/input/db.sqlite"
BACKUP_DIR="$HOME/backups/publii"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Kopiere Datenbank
cp "$DB_PATH" "$BACKUP_DIR/${SITE}_${TIMESTAMP}.sqlite"

# Behalte nur letzte 30 Backups
cd "$BACKUP_DIR"
ls -t | tail -n +31 | xargs -r rm

echo "✓ Backup erstellt: ${SITE}_${TIMESTAMP}.sqlite"
```

**Cron Setup:**
```bash
chmod +x ~/bin/publii-backup.sh
crontab -e
# Täglich um 2 Uhr: 0 2 * * * ~/bin/publii-backup.sh
```

## Beispiel 9: Claude Code Integration

Verwende publii-mcp direkt in Claude Code:

```markdown
User: Erstelle einen Blogpost über Python 3.13

Claude (mit publii-mcp):
- Verwendet list_authors um gültige Autor-ID zu finden
- Generiert Post-Text
- Ruft create_post auf:
  - title: "Was ist neu in Python 3.13?"
  - text: [generierter Inhalt]
  - status: "draft"
  - author_id: 1
- Antwortet mit Post-ID und Slug
```

**Vorteile:**
- Direkte Content-Erstellung ohne Publii-UI
- Batch-Operationen möglich
- Integration mit anderen Tools/APIs

## Beispiel 10: RSS-to-Publii

Importiere RSS-Feed als Posts:

```python
import feedparser
from publii_mcp.db import PubliiDB

# Parse RSS Feed
feed = feedparser.parse("https://example.com/feed.xml")
db = PubliiDB(site="aggregator")

for entry in feed.entries[:10]:  # Nur erste 10
    post = db.create_post(
        title=entry.title,
        text=f"""
        <p><em>Quelle: <a href="{entry.link}">{entry.link}</a></em></p>
        {entry.summary}
        """,
        author_id=1,
        status="draft",
        created_at=entry.published,  # RFC 2822 Format
    )
    print(f"✓ Importiert: {post['title']}")
```

## Best Practices

### 1. Immer Drafts verwenden

```python
# ✓ Gut: Erst als Draft erstellen
post = db.create_post(..., status="draft")
# Review im Publii
# Dann veröffentlichen
db.update_post(post_id=post["id"], status="published")

# ✗ Vermeiden: Direkt veröffentlichen ohne Review
post = db.create_post(..., status="published")
```

### 2. Error Handling

```python
from publii_mcp.db import PubliiDB

try:
    db = PubliiDB(site="my-site")
    post = db.create_post(...)
except ValueError as e:
    print(f"Fehler: {e}")
    # Logge oder handle Error
```

### 3. Batch-Operationen mit Transaction-Simulation

```python
# SQLite unterstützt Transaktionen, aber PubliiDB nutzt einzelne Connections
# Für Batch-Ops: Sammle Errors und rolle manuell zurück

created_ids = []
try:
    for item in items:
        post = db.create_post(...)
        created_ids.append(post["id"])
except Exception as e:
    # Rollback: Lösche erstellte Posts
    for post_id in created_ids:
        db.delete_post(post_id)
    raise
```

## Weitere Ressourcen

- **API-Referenz:** [docs/api.md](api.md)
- **Troubleshooting:** [docs/troubleshooting.md](troubleshooting.md)
- **Development:** [docs/development.md](development.md)
