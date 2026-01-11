# API-Referenz

Vollständige Dokumentation aller 14 MCP-Tools des publii-mcp Servers.

## Sites

### list_sites

Listet alle verfügbaren Publii-Sites auf.

**Parameter:** Keine

**Rückgabe:** `list[dict]` - Liste von Site-Objekten mit `name` und `has_db`

**Beispiel:**
```python
list_sites()
# [{"name": "blog", "has_db": True}, {"name": "portfolio", "has_db": True}]
```

---

### get_site_info

Gibt Details zu einer spezifischen Site zurück.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `site` | `str` | Nein | Site-Name (verwendet Default wenn nicht angegeben) |

**Rückgabe:** `dict` mit Site-Informationen

**Beispiel:**
```python
get_site_info("blog")
# {"name": "blog", "path": "/path/to/db.sqlite", ...}
```

---

## Posts

### list_posts

Listet Blog-Posts einer Site auf.

**Parameter:**

| Name | Typ | Erforderlich | Default | Beschreibung |
|------|-----|--------------|---------|--------------|
| `site` | `str` | Nein | Default-Site | Site-Name |
| `status` | `str` | Nein | `"all"` | Filter: `"all"`, `"published"`, `"draft"` |
| `limit` | `int` | Nein | `20` | Maximale Anzahl |

**Rückgabe:** `list[dict]` - Liste von Post-Objekten (ohne Content)

**Beispiel:**
```python
list_posts(site="blog", status="published", limit=10)
```

---

### get_post

Ruft einen vollständigen Post ab (inkl. Content).

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `post_id` | `int` | Ja | Post-ID |
| `site` | `str` | Nein | Site-Name |

**Rückgabe:** `dict` - Vollständiges Post-Objekt mit `content`

**Fehler:** `ValueError` wenn Post nicht existiert

---

### create_post

Erstellt einen neuen Blog-Post.

**Parameter:**

| Name | Typ | Erforderlich | Default | Beschreibung |
|------|-----|--------------|---------|--------------|
| `title` | `str` | Ja | - | Post-Titel |
| `content` | `str` | Ja | - | HTML-Content |
| `site` | `str` | Nein | Default-Site | Site-Name |
| `slug` | `str` | Nein | Auto-generiert | URL-Slug |
| `status` | `str` | Nein | `"draft"` | `"draft"` oder `"published"` |
| `author_id` | `int` | Nein | `1` | Autor-ID |

**Rückgabe:** `dict` - Erstellter Post

**Fehler:** `ValueError` wenn Autor nicht existiert

**Beispiel:**
```python
create_post(
    title="Mein neuer Artikel",
    content="<p>Inhalt hier...</p>",
    site="blog",
    status="draft"
)
```

---

### update_post

Aktualisiert einen bestehenden Post.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `post_id` | `int` | Ja | Post-ID |
| `site` | `str` | Nein | Site-Name |
| `title` | `str` | Nein | Neuer Titel |
| `content` | `str` | Nein | Neuer Content |
| `status` | `str` | Nein | Neuer Status |

**Rückgabe:** `dict` - Aktualisierter Post

**Fehler:** `ValueError` wenn Post nicht existiert

---

### delete_post

Löscht einen Post und alle zugehörigen Daten.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `post_id` | `int` | Ja | Post-ID |
| `site` | `str` | Nein | Site-Name |

**Rückgabe:** `dict` - `{"deleted": True, "id": post_id}`

**Hinweis:** Löscht auch verknüpfte Tags, Images und Additional Data.

---

## Pages

### list_pages

Listet statische Seiten einer Site auf.

**Parameter:**

| Name | Typ | Erforderlich | Default | Beschreibung |
|------|-----|--------------|---------|--------------|
| `site` | `str` | Nein | Default-Site | Site-Name |
| `status` | `str` | Nein | `"all"` | Filter: `"all"`, `"published"`, `"draft"` |
| `limit` | `int` | Nein | `20` | Maximale Anzahl |

**Rückgabe:** `list[dict]` - Liste von Page-Objekten

---

### get_page

Ruft eine vollständige Page ab.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `page_id` | `int` | Ja | Page-ID |
| `site` | `str` | Nein | Site-Name |

**Rückgabe:** `dict` - Vollständiges Page-Objekt

**Fehler:** `ValueError` wenn Page nicht existiert

---

### create_page

Erstellt eine neue statische Seite.

**Parameter:**

| Name | Typ | Erforderlich | Default | Beschreibung |
|------|-----|--------------|---------|--------------|
| `title` | `str` | Ja | - | Page-Titel |
| `content` | `str` | Ja | - | HTML-Content |
| `site` | `str` | Nein | Default-Site | Site-Name |
| `slug` | `str` | Nein | Auto-generiert | URL-Slug |
| `status` | `str` | Nein | `"draft"` | `"draft"` oder `"published"` |
| `author_id` | `int` | Nein | `1` | Autor-ID |

**Rückgabe:** `dict` - Erstellte Page

---

### update_page

Aktualisiert eine bestehende Page.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `page_id` | `int` | Ja | Page-ID |
| `site` | `str` | Nein | Site-Name |
| `title` | `str` | Nein | Neuer Titel |
| `content` | `str` | Nein | Neuer Content |
| `status` | `str` | Nein | Neuer Status |

**Rückgabe:** `dict` - Aktualisierte Page

---

### delete_page

Löscht eine Page.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `page_id` | `int` | Ja | Page-ID |
| `site` | `str` | Nein | Site-Name |

**Rückgabe:** `dict` - `{"deleted": True, "id": page_id}`

---

## Metadata

### list_tags

Listet alle Tags einer Site auf.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `site` | `str` | Nein | Site-Name |

**Rückgabe:** `list[dict]` - Liste von Tag-Objekten mit `id`, `name`, `slug`

---

### list_authors

Listet alle Autoren einer Site auf.

**Parameter:**

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `site` | `str` | Nein | Site-Name |

**Rückgabe:** `list[dict]` - Liste von Author-Objekten mit `id`, `name`, `email`, etc.

---

## Gemeinsame Datenstrukturen

### Post/Page Objekt

```python
{
    "id": 1,
    "title": "Mein Titel",
    "slug": "mein-titel",
    "status": "draft",  # oder "published"
    "created_at": "2024-01-15T10:30:00",
    "modified_at": "2024-01-15T12:00:00",
    "author_id": 1,
    "content": "<p>...</p>",  # nur bei get_post/get_page
    "featured_image_id": null
}
```

### Tag Objekt

```python
{
    "id": 1,
    "name": "Python",
    "slug": "python",
    "description": "Python-Artikel"
}
```

### Author Objekt

```python
{
    "id": 1,
    "name": "Max Mustermann",
    "username": "max",
    "email": "max@example.com"
}
```
