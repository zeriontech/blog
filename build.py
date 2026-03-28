#!/usr/bin/env python3
"""Build the Zerion blog static site from markdown content files.

Usage:
    python3 build.py              # Build into public/
    python3 build.py --serve      # Build and start local server on port 3000
"""

import json
import html
import os
import re
import sys
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
POSTS_DIR = CONTENT_DIR / "posts"
PAGES_DIR = CONTENT_DIR / "pages"
AUTHORS_FILE = CONTENT_DIR / "authors.json"
OUTPUT_DIR = ROOT / "public"

GHOST_URL = "https://zerion.io/blog"

# ────────────────────────────────────────────────────────────────────────
# Logo SVG (currentColor so it inherits text color)
# ────────────────────────────────────────────────────────────────────────

ZERION_LOGO_SVG = '<svg width="132" height="32" viewBox="0 0 132 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M94.8044 3.09c0 1.3-1.09 2.35-2.41 2.35-1.35 0-2.47-1.05-2.47-2.35s1.12-2.35 2.47-2.35c1.32 0 2.41 1.05 2.41 2.35zm-.9 20.82h-3.08c-.26 0-.42-.16-.42-.41V8.45c0-.25.16-.41.42-.41h3.08c.29 0 .42.16.42.41v15.04c0 .25-.16.41-.42.41zM62.16 14.26h7.86c.19 0 .32-.13.29-.32-.29-1.84-2.09-3.14-4.33-3.14-2.18 0-3.92 1.3-4.17 3.11-.03.19.13.35.35.35zm-4.33 1.62c0-4.73 3.47-8.19 8.18-8.19 4.59 0 8.38 3.08 8.05 8.82 0 .35-.26.6-.64.6H62.06c-.22 0-.32.16-.29.38.16 2.03 2.02 3.59 4.3 3.59 1.67 0 3.08-.76 3.79-2.03.1-.22.22-.32.45-.32h3.05c.26 0 .42.19.32.51-.93 2.98-3.88 5.01-7.32 5.01-5.04 0-8.53-3.43-8.53-8.37zm-1.75 8.03H43.18c-.26 0-.42-.16-.41-.41v-1.87c0-.26.06-.51.26-.73l7.96-9.2c.16-.19.03-.45-.22-.45h-7.35c-.26 0-.42-.16-.42-.41V8.45c0-.25.16-.41.42-.41h12.35c.26 0 .42.16.42.41v1.81c0 .32-.1.54-.32.8l-7.99 9.2c-.16.19-.03.45.22.45h7.96c.26 0 .42.16.42.41v2.38c0 .25-.16.41-.42.41zm31.24-15.87h-2.12c-1.96 0-3.21.7-3.88 2.19-.19.41-.74.32-.74-.1V8.45c0-.25-.16-.41-.42-.41h-2.7c-.25 0-.41.16-.41.41v15.04c0 .25.16.41.42.41h3.08c.29 0 .42-.19.42-.41V12.77c0-.38.29-.76.7-.76h5.65c.26 0 .42-.16.42-.41V8.46c0-.26-.16-.42-.42-.42zm18.19 12.88c-2.66 0-4.56-2.1-4.56-5.02s1.9-4.89 4.56-4.89 4.59 2.03 4.59 4.89-1.93 5.02-4.59 5.02zm.03 3.33c4.94 0 8.47-3.49 8.47-8.38 0-4.76-3.53-8.19-8.47-8.19-4.97 0-8.54 3.43-8.54 8.19 0 4.89 3.56 8.38 8.54 8.38zM131.97 14.2v9.3c0 .25-.16.41-.42.41h-3.08c-.26 0-.42-.16-.42-.41v-8.6c0-2.48-1.25-3.87-3.47-3.87-2.57 0-3.95 1.46-3.95 4.28v8.19c0 .25-.16.41-.42.41h-3.08c-.26 0-.42-.16-.42-.41V8.45c0-.25.16-.41.42-.41h2.7c.25 0 .42.16.42.44v1.21c0 .38.39.48.64.16 1.09-1.4 2.79-2.16 4.81-2.16 3.72 0 6.26 2.29 6.26 6.51z" fill="currentColor"/><path fill-rule="evenodd" clip-rule="evenodd" d="M8.89 31.46h13.66c4.91 0 8.89-3.94 8.89-8.79V9.15c0-4.86-3.98-8.79-8.89-8.79H8.89C3.98.36 0 4.3 0 9.15v13.51c0 4.86 3.98 8.79 8.89 8.79zm14.16-9.66c-2.8-1.73-6.52-3.84-9.57-5.48-.74-.4-1.73-.25-2.34.61-1.13 1.6-2.49 3.62-3.42 5.21-.39.64.12 1.49.9 1.49h13.84c1 0 1.42-1.25.59-1.83zm-5.12-5.99c-2.95-1.56-7.09-3.93-10.03-5.72-.91-.55-.55-1.89.51-1.88h15.37c.85 0 1.28.87.92 1.48-1.22 2.05-2.59 4.12-3.73 5.66-.51.69-1.54.85-2.28.46h-.76z" fill="currentColor"/></svg>'

# Dashed Z triangles only (no outer rounded rect)
ZERION_Z_DASHED = '<svg viewBox="0 0 32 32" fill="none"><path d="M17.94 15.79C14.98 14.23 10.84 11.86 7.9 10.07C6.99 9.52 7.35 8.19 8.41 8.19C10.15 8.19 12.97 8.19 15.78 8.19C18.56 8.19 21.33 8.19 23.01 8.19C23.86 8.19 24.3 9.06 23.94 9.66C22.72 11.72 21.35 13.79 20.21 15.34C19.7 16.02 18.68 16.18 17.94 15.79Z" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2 2" fill="none"/><path d="M23.05 21.8C20.25 20.07 16.54 17.95 13.48 16.32C12.74 15.92 11.75 16.07 11.14 16.93C10 18.53 8.64 20.55 7.71 22.14C7.33 22.78 7.84 23.63 8.62 23.63L22.46 23.63C23.46 23.63 23.88 22.38 23.05 21.8Z" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2 2" fill="none"/></svg>'

# Z letterpress tiling pattern – dense, tiny dashes, very faint
import base64 as _b64
_z_tile_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><g transform="translate(6,6) scale(0.625)" opacity="0.18"><path d="M17.94 15.79C14.98 14.23 10.84 11.86 7.9 10.07C6.99 9.52 7.35 8.19 8.41 8.19C10.15 8.19 12.97 8.19 15.78 8.19C18.56 8.19 21.33 8.19 23.01 8.19C23.86 8.19 24.3 9.06 23.94 9.66C22.72 11.72 21.35 13.79 20.21 15.34C19.7 16.02 18.68 16.18 17.94 15.79Z" stroke="black" stroke-width="1.2" stroke-dasharray="0.8 1" fill="none"/><path d="M23.05 21.8C20.25 20.07 16.54 17.95 13.48 16.32C12.74 15.92 11.75 16.07 11.14 16.93C10 18.53 8.64 20.55 7.71 22.14C7.33 22.78 7.84 23.63 8.62 23.63L22.46 23.63C23.46 23.63 23.88 22.38 23.05 21.8Z" stroke="black" stroke-width="1.2" stroke-dasharray="0.8 1" fill="none"/></g></svg>'
Z_TILE_DATA_URI = 'url("data:image/svg+xml;base64,' + _b64.b64encode(_z_tile_svg.encode()).decode() + '")'

ZERION_ICON_SVG = '<svg width="32" height="32" viewBox="0 0 32 32" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M8.89 31.46h13.66c4.91 0 8.89-3.94 8.89-8.79V9.15c0-4.86-3.98-8.79-8.89-8.79H8.89C3.98.36 0 4.3 0 9.15v13.51c0 4.86 3.98 8.79 8.89 8.79zm14.16-9.66c-2.8-1.73-6.52-3.84-9.57-5.48-.74-.4-1.73-.25-2.34.61-1.13 1.6-2.49 3.62-3.42 5.21-.39.64.12 1.49.9 1.49h13.84c1 0 1.42-1.25.59-1.83zm-5.12-5.99c-2.95-1.56-7.09-3.93-10.03-5.72-.91-.55-.55-1.89.51-1.88h15.37c.85 0 1.28.87.92 1.48-1.22 2.05-2.59 4.12-3.73 5.66-.51.69-1.54.85-2.28.46h-.76z" fill="currentColor"/></svg>'


# ────────────────────────────────────────────────────────────────────────
# Markdown / frontmatter parsing
# ────────────────────────────────────────────────────────────────────────

def parse_frontmatter(text):
    """Parse YAML-ish frontmatter between --- delimiters. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    fm_text = text[4:end]
    body = text[end + 4:].strip()

    meta = {}
    current_key = None
    current_list = None

    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # List item under current key
        if stripped.startswith("- ") and current_list is not None:
            val = stripped[2:].strip()
            # Check if it's a dict-style list item (key: value)
            if ": " in val and not val.startswith('"'):
                k, v = val.split(": ", 1)
                k = k.strip()
                v = v.strip().strip('"')
                if not current_list or not isinstance(current_list[-1], dict):
                    current_list.append({})
                current_list[-1][k] = v
            else:
                val = val.strip('"')
                current_list.append(val)
            continue

        # Sub-key of a dict in a list
        if line.startswith("    ") and current_list is not None and current_list and isinstance(current_list[-1], dict):
            if ": " in stripped:
                k, v = stripped.split(": ", 1)
                current_list[-1][k.strip()] = v.strip().strip('"')
            continue

        # Top-level key
        if ": " in stripped or stripped.endswith(":"):
            if ": " in stripped:
                k, v = stripped.split(": ", 1)
                k = k.strip()
                v = v.strip().strip('"')
                if v:
                    meta[k] = v
                    current_key = k
                    current_list = None
                else:
                    # Empty value = start of list
                    meta[k] = []
                    current_key = k
                    current_list = meta[k]
            else:
                k = stripped.rstrip(":")
                meta[k] = []
                current_key = k
                current_list = meta[k]

    return meta, body


def load_posts():
    """Load all markdown posts from content/posts/."""
    posts = []
    for md_file in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        text = md_file.read_text()
        meta, body = parse_frontmatter(text)
        if not meta.get("slug"):
            continue

        # Build the post dict matching what templates expect
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        tag_names = [t if isinstance(t, str) else t.get("name", "") for t in tags]

        authors = meta.get("authors", [])
        if isinstance(authors, str):
            authors = [{"name": authors, "slug": "", "avatar": ""}]

        excerpt = meta.get("excerpt", "")
        if not excerpt and body:
            # Strip HTML for excerpt
            plain = re.sub(r'<[^>]+>', '', body)
            plain = plain.strip().replace("\n", " ")
            if len(plain) > 180:
                excerpt = plain[:180].rsplit(" ", 1)[0]
            else:
                excerpt = plain

        post = {
            "id": meta.get("slug"),
            "title": meta.get("title", "Untitled"),
            "slug": meta["slug"],
            "excerpt": excerpt,
            "html": body,
            "feature_image": meta.get("feature_image", ""),
            "featured": meta.get("featured", False),
            "published_at": meta.get("published_at", meta.get("date", "")),
            "date_display": format_date(meta.get("published_at", meta.get("date", ""))),
            "reading_time": reading_time(body),
            "authors": [{
                "name": a.get("name", "") if isinstance(a, dict) else a,
                "slug": a.get("slug", "") if isinstance(a, dict) else "",
                "profile_image": a.get("avatar", "") if isinstance(a, dict) else "",
            } for a in authors],
            "primary_tag": get_primary_tag(tag_names),
            "category": get_category(tag_names),
            "tags": [{"name": t, "slug": t.lower().replace(" ", "-")} for t in tag_names],
        }
        posts.append(post)

    posts.sort(key=lambda x: x["published_at"], reverse=True)
    return posts


def load_pages():
    """Load all markdown pages from content/pages/."""
    pages = []
    for md_file in sorted(PAGES_DIR.glob("*.md")):
        text = md_file.read_text()
        meta, body = parse_frontmatter(text)
        if not meta.get("slug"):
            continue
        pages.append({
            "title": meta.get("title", "Untitled"),
            "slug": meta["slug"],
            "html": body,
            "feature_image": meta.get("feature_image", ""),
        })
    return pages


def load_authors():
    """Load authors from content/authors.json."""
    if AUTHORS_FILE.exists():
        with open(AUTHORS_FILE) as f:
            return json.load(f)
    return {}


# ────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────

def format_date(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return str(iso_str)


def reading_time(text):
    if not text:
        return "1 min read"
    plain = re.sub(r'<[^>]+>', '', text)
    words = len(plain.split())
    minutes = max(1, round(words / 250))
    return f"{minutes} min read"


def get_primary_tag(tag_names):
    priority = ["Zerion Wallet", "Zerion API", "Learn", "DeFi", "product updates", "NFTs"]
    display_map = {"Zerion API": "API", "Zerion Wallet": "Wallet"}
    for p in priority:
        if p in tag_names:
            return display_map.get(p, p)
    for t in tag_names:
        if not t.startswith("#"):
            return display_map.get(t, t)
    return None


def get_category(tag_names):
    s = set(tag_names)
    if "Zerion API" in s:
        return "zerion-api"
    if "Zerion Wallet" in s or "product updates" in s:
        return "zerion-wallet"
    if "Learn" in s:
        return "learn"
    if "DeFi" in s or "Decentralized Finance" in s:
        return "defi"
    return "all"


def fix_internal_links(text):
    """Rewrite internal Ghost links to relative paths."""
    if not text:
        return ""
    text = re.sub(r'href="https://zerion\.io/blog/([^"]*)"', r'href="/\1"', text)
    return text


# ────────────────────────────────────────────────────────────────────────
# HTML generators
# ────────────────────────────────────────────────────────────────────────


def render(template, **kwargs):
    """Replace %%key%% placeholders in template."""
    result = template
    for k, v in kwargs.items():
        result = result.replace("%%" + k + "%%", str(v))
    return result

def generate_post_html(post):
    authors_html = ""
    for a in post["authors"]:
        avatar = f'<img src="{html.escape(a["profile_image"])}" alt="" class="author-avatar">' if a["profile_image"] else '<div class="author-avatar-placeholder"></div>'
        slug = a.get("slug", "")
        if slug:
            authors_html += f'<div class="author"><a href="/author/{html.escape(slug)}/" class="author-link">{avatar}<span class="author-name">{html.escape(a["name"])}</span></a></div>'
        else:
            authors_html += f'<div class="author">{avatar}<span class="author-name">{html.escape(a["name"])}</span></div>'

    hero_img = ""
    if post["feature_image"]:
        hero_img = f'<div class="hero-wrap"><img src="{html.escape(post["feature_image"])}" alt="" class="hero-image"></div>'

    tags_html = ""
    if post["tags"]:
        tags_html = '<div class="post-tags">' + "".join(
            f'<span class="tag-pill">{html.escape(t["name"])}</span>' for t in post["tags"][:5]
        ) + '</div>'

    content = fix_internal_links(post["html"])

    return render(POST_TEMPLATE,
        title=html.escape(post["title"]),
        title_raw=post["title"],
        date=post["date_display"],
        reading_time=post["reading_time"],
        primary_tag=html.escape(post["primary_tag"] or ""),
        authors=authors_html,
        hero_image=hero_img,
        content=content,
        tags=tags_html,
        logo=ZERION_LOGO_SVG,
    )


def generate_card_html(post, featured=False):
    img = ""
    if post["feature_image"]:
        img = f'<div class="card-img"><img src="{html.escape(post["feature_image"])}" alt="" loading="lazy"></div>'

    tag = ""
    if post["primary_tag"]:
        tag = f'<span class="card-tag">{html.escape(post["primary_tag"])}</span>'

    author_name = post["authors"][0]["name"] if post["authors"] else "Zerion Team"
    cls = "card card--featured" if featured else "card"

    excerpt = ""
    if post["excerpt"]:
        ex_text = post["excerpt"].rstrip('.').rstrip('\u2026').rstrip('.').strip()
        if ex_text:
            max_lines = 3 if featured else 2
            excerpt = f'<p class="card-excerpt" style="-webkit-line-clamp:{max_lines}">{html.escape(ex_text)}</p>'

    arrow = '<div class="card-arrow"><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3.3 12.7L12.7 3.3M12.7 3.3H5.3M12.7 3.3v7.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'

    return f'''<a href="/{html.escape(post["slug"])}/" class="{cls}" data-category="{post["category"]}">
{img}<div class="card-body">{tag}<h2 class="card-title">{html.escape(post["title"])}</h2>{excerpt}<div class="card-meta"><span>{html.escape(author_name)}</span><span class="sep">&middot;</span><time>{post["date_display"]}</time></div></div>{arrow}</a>'''


def generate_index(posts):
    featured = [p for p in posts if p["feature_image"]][:3]
    if len(featured) < 3:
        featured = posts[:3]
    featured_set = {p["id"] for p in featured}
    remaining = [p for p in posts if p["id"] not in featured_set]

    return render(INDEX_TEMPLATE,
        featured_cards="\n".join(generate_card_html(p, True) for p in featured),
        post_cards="\n".join(generate_card_html(p) for p in remaining),
        total_posts=len(posts),
        logo=ZERION_LOGO_SVG,
    )


def generate_changelog_entry(post):
    img = ""
    if post["feature_image"]:
        img = f'<a href="/{html.escape(post["slug"])}/" class="cl-img"><img src="{html.escape(post["feature_image"])}" alt="" loading="lazy"></a>'
    excerpt = ""
    if post["excerpt"]:
        excerpt = f'<p class="cl-excerpt">{html.escape(post["excerpt"])}</p>'
    return f'''<article class="cl-entry">
<div class="cl-date-col"><time class="cl-date">{post["date_display"]}</time></div>
<div class="cl-line-col"><div class="cl-dot"></div></div>
<div class="cl-content">
  {img}
  <a href="/{html.escape(post["slug"])}/" class="cl-title">{html.escape(post["title"])}</a>
  {excerpt}
</div>
</article>'''


def generate_changelog(changelog_posts):
    return render(CHANGELOG_TEMPLATE,
        entries="\n".join(generate_changelog_entry(p) for p in changelog_posts),
        total=len(changelog_posts),
        logo=ZERION_LOGO_SVG,
    )


def generate_author_page(author_info, author_posts):
    cards = "\n".join(generate_card_html(p) for p in author_posts)
    name = html.escape(author_info.get("name", ""))
    bio = html.escape(author_info.get("bio", ""))
    avatar = ""
    img = author_info.get("profile_image", "")
    if img:
        avatar = f'<img src="{html.escape(img)}" alt="" style="width:64px;height:64px;border-radius:50%;object-fit:cover;margin-bottom:12px">'

    return render(INDEX_TEMPLATE,
        featured_cards="",
        post_cards=cards,
        total_posts=len(author_posts),
        logo=ZERION_LOGO_SVG,
    ).replace(
        '<title>Zerion Blog</title>',
        f'<title>{name} \u2013 Zerion Blog</title>',
    )


def generate_tag_page(tag_name, tag_posts):
    cards = "\n".join(generate_card_html(p) for p in tag_posts)
    name = html.escape(tag_name)
    return render(INDEX_TEMPLATE,
        featured_cards="",
        post_cards=cards,
        total_posts=len(tag_posts),
        logo=ZERION_LOGO_SVG,
    ).replace(
        '<title>Zerion Blog</title>',
        f'<title>{name} \u2013 Zerion Blog</title>',
    )


def generate_static_page(page):
    content = fix_internal_links(page["html"])
    hero = ""
    if page.get("feature_image"):
        hero = f'<img src="{html.escape(page["feature_image"])}" alt="" class="hero-image">'
    return render(POST_TEMPLATE,
        title=html.escape(page["title"]),
        title_raw=page["title"],
        date="",
        reading_time="",
        primary_tag="",
        authors="",
        hero_image=hero,
        content=content,
        tags="",
        logo=ZERION_LOGO_SVG,
    )


# ────────────────────────────────────────────────────────────────────────
# CSS shared across templates
# ────────────────────────────────────────────────────────────────────────

CSS_VARS = '''
:root{
  --bg:#F7F7F8;--surface:#FFF;--text:#0F0F0F;--text2:#5F5F5F;--text3:#9B9B9B;
  --accent:#2962EF;--accent-light:rgba(41,98,239,.08);--border:rgba(0,0,0,.08);
  --border-dashed:rgba(0,0,0,.06);--hover:rgba(0,0,0,.018);
  --r:16px;--rs:10px;--max:1240px;--nav-h:60px;
  --font:'Inter',ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}'''

CSS_BASE = '''
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
''' + CSS_VARS + '''
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;line-height:1.5}
/* Z watermark layer – sits behind all content */
.z-bg{position:fixed;inset:0;background-image:''' + Z_TILE_DATA_URI + ''';background-size:32px 32px;pointer-events:none;
  -webkit-mask-image:radial-gradient(circle 300px at var(--mx,50%) var(--my,50%),black 0%,rgba(0,0,0,.25) 50%,rgba(0,0,0,.08) 100%);
  mask-image:radial-gradient(circle 300px at var(--mx,50%) var(--my,50%),black 0%,rgba(0,0,0,.25) 50%,rgba(0,0,0,.08) 100%)}
.page{position:relative;z-index:1}
'''

CSS_NAV = '''
.nav{position:sticky;top:0;z-index:100;height:var(--nav-h);display:flex;align-items:center;padding:0 32px;background:rgba(247,247,248,.85);backdrop-filter:saturate(180%) blur(16px);-webkit-backdrop-filter:saturate(180%) blur(16px);border-bottom:1px solid var(--border)}
.nav-in{max-width:var(--max);width:100%;margin:0 auto;display:flex;align-items:center;gap:32px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);flex-shrink:0}
.logo svg{height:22px;width:auto}
.logo-sep{width:1px;height:20px;background:var(--border)}
.logo span{font-size:14px;font-weight:600;color:var(--text2);letter-spacing:-.01em}
.pills{display:flex;gap:2px;flex:1;justify-content:center;overflow:visible;scrollbar-width:none;padding:4px 0}
.pills::-webkit-scrollbar{display:none}
.pill{padding:7px 14px;border-radius:999px;font-size:13px;font-weight:500;border:none;background:0;color:var(--text2);cursor:pointer;transition:color .2s,background .2s,transform .15s cubic-bezier(.34,1.56,.64,1),box-shadow .2s;white-space:nowrap;font-family:inherit;text-decoration:none;display:inline-flex;align-items:center}
.pill:hover{color:var(--text);background:rgba(0,0,0,.05);transform:translateY(-1px)}
.pill:active{transform:scale(.96);transition-duration:.1s}
.pill.on{background:var(--text);color:#fff;box-shadow:0 1px 4px rgba(0,0,0,.1)}
.search-wrap{position:relative;flex-shrink:0}
.search-wrap svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--text3);pointer-events:none}
.search{padding:8px 14px 8px 36px;border-radius:999px;border:1.5px solid var(--border);background:var(--surface);font:13px/1 var(--font);color:var(--text);width:180px;outline:0;transition:.2s}
.search:focus{border-color:var(--accent);width:240px;box-shadow:0 0 0 3px rgba(41,98,239,.1)}
'''

CSS_FOOTER = '''
.footer{border-top:1px solid var(--border);margin-top:20px}
.footer-in{max-width:var(--max);margin:0 auto;padding:40px 32px;display:flex;justify-content:space-between;align-items:center}
.footer-left{display:flex;align-items:center;gap:12px}
.footer-left svg{height:18px;color:var(--text3)}
.footer-copy{font-size:12px;color:var(--text3)}
.footer-links{display:flex;gap:24px}
.footer-links a{font-size:13px;color:var(--text2);text-decoration:none;transition:color .15s}
.footer-links a:hover{color:var(--text)}
'''

SPOTLIGHT_JS = '<script>document.addEventListener("mousemove",e=>{document.body.style.setProperty("--mx",e.clientX+"px");document.body.style.setProperty("--my",e.clientY+"px")})</script>'

FOOTER_HTML = f'''<footer class="footer">
<div class="footer-in">
  <div class="footer-left">
    {ZERION_ICON_SVG}
    <span class="footer-copy">&copy; 2026 Zerion. All rights reserved.</span>
  </div>
  <div class="footer-links">
    <a href="https://zerion.io">Website</a>
    <a href="https://zerion.io/api">API</a>
    <a href="https://x.com/zerion">X / Twitter</a>
    <a href="https://discord.gg/zerion">Discord</a>
    <a href="https://github.com/zeriontech">GitHub</a>
  </div>
</div>
</footer>
''' + SPOTLIGHT_JS

NAV_PILLS_HTML = '''<nav class="nav">
<div class="nav-in">
  <a href="/" class="logo">
    %%logo%%
    <div class="logo-sep"></div>
    <span>Blog</span>
  </a>
  <div class="pills">
    <a href="/" class="pill{all_active}" data-f="all">All Posts</a>
    <a href="/?c=zerion-wallet" class="pill{wallet_active}" data-f="zerion-wallet">Wallet</a>
    <a href="/?c=zerion-api" class="pill{api_active}" data-f="zerion-api">API</a>
    <a href="/?c=learn" class="pill{learn_active}" data-f="learn">Learn</a>
    <a href="/?c=defi" class="pill{defi_active}" data-f="defi">DeFi</a>
    <a href="/changelog/" class="pill{changelog_active}">Changelog</a>
  </div>
  <div class="search-wrap">
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M7.333 12.667A5.333 5.333 0 107.333 2a5.333 5.333 0 000 10.667zM14 14l-2.9-2.9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <input type="text" class="search" placeholder="Search posts\u2026" id="q">
  </div>
</div>
</nav>'''


def nav_html(active="all"):
    pills = {"all": "", "wallet": "", "api": "", "learn": "", "defi": "", "changelog": ""}
    if active in pills:
        pills[active] = " on"
    return NAV_PILLS_HTML.format(
        logo=ZERION_LOGO_SVG,
        all_active=pills["all"],
        wallet_active=pills["wallet"],
        api_active=pills["api"],
        learn_active=pills["learn"],
        defi_active=pills["defi"],
        changelog_active=pills["changelog"],
    )


# ────────────────────────────────────────────────────────────────────────
# TEMPLATES
# ────────────────────────────────────────────────────────────────────────

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zerion Blog</title>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
<style>
''' + CSS_BASE + CSS_NAV + '''

/* ─── Z DECO (unused, pattern is on cards now) ─── */

/* ─── SECTIONS ─── */
.sec-head{display:flex;align-items:center;gap:12px;padding:32px 0 20px}
.sec-label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--text3)}

/* ─── SECTIONS ─── */
.container{max-width:var(--max);margin:0 auto;padding:0 32px}

/* ─── GRID with + intersection markers ─── */
.grid-wrap{position:relative}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border-radius:var(--r);overflow:hidden;position:relative}

/* + signs at grid intersections */
.grid-wrap::before,.grid-wrap::after{content:'+';position:absolute;font-size:12px;font-weight:300;color:var(--text3);z-index:2;line-height:1;opacity:.3;pointer-events:none}
.grid-wrap::before{top:-7px;right:-7px}
.grid-wrap::after{bottom:-7px;left:-7px}

/* ─── CARDS ─── */
.card{display:flex;flex-direction:column;background:var(--surface);text-decoration:none;color:inherit;transition:background .3s ease;position:relative;overflow:hidden}
.card:hover{background:#FCFCFD}

/* Card hover texture (subtle) */
.card::before{content:'';position:absolute;inset:0;background:transparent;pointer-events:none;z-index:0}

/* Corner bracket decoration on hover */
.card::after{content:'';position:absolute;top:10px;right:10px;width:10px;height:10px;border-top:1px solid rgba(0,0,0,.12);border-right:1px solid rgba(0,0,0,.12);opacity:0;transition:opacity .3s ease,transform .3s ease;transform:translate(2px,-2px);pointer-events:none;z-index:2}
.card:hover::after{opacity:1;transform:translate(0,0)}

/* Card image */
.card-img{aspect-ratio:16/9;overflow:hidden;background:linear-gradient(135deg,#f0f0f2,#e8e8ec);position:relative;z-index:1}
.card-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s cubic-bezier(.25,.46,.45,.94)}
.card:hover .card-img img{transform:scale(1.03)}

/* Dashed circle decoration on image */
.card-img::after{content:'';position:absolute;bottom:-16px;right:-16px;width:56px;height:56px;border:1px dashed rgba(255,255,255,.25);border-radius:50%;opacity:0;transition:opacity .4s ease,transform .4s ease;transform:scale(.85);pointer-events:none;z-index:2}
.card:hover .card-img::after{opacity:1;transform:scale(1)}

/* Card body */
.card-body{padding:28px 28px 24px;display:flex;flex-direction:column;flex:1;position:relative;z-index:1}
.card--featured .card-body{padding:32px 32px 28px}

.card-tag{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);margin-bottom:10px;display:inline-flex;align-items:center;gap:6px}
.card-tag::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent);opacity:.4}

.card-title{font-size:17px;font-weight:600;line-height:1.35;letter-spacing:-.015em;margin-bottom:8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .25s}
.card:hover .card-title{color:#1a1a1a}
.card--featured .card-title{font-size:22px;letter-spacing:-.025em;-webkit-line-clamp:3}

.card-excerpt{font-size:14px;line-height:1.5;color:var(--text2);margin-bottom:16px;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}

.card-meta{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text3);margin-top:auto;padding-top:16px;border-top:1px dashed var(--border-dashed)}
.card-meta .sep{opacity:.3}

/* Arrow indicator on card hover */
.card-arrow{position:absolute;bottom:24px;right:28px;width:26px;height:26px;border-radius:50%;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;opacity:0;transform:translateX(-6px);transition:opacity .3s ease,transform .3s ease;z-index:2}
.card:hover .card-arrow{opacity:.6;transform:translateX(0)}
.card-arrow svg{color:var(--text3)}

/* ─── LOAD MORE ─── */
.more-wrap{padding:56px 0 88px;text-align:center}
.more-btn{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;border-radius:999px;border:1.5px solid var(--border);background:var(--surface);font:14px/1.2 var(--font);font-weight:500;color:var(--text);cursor:pointer;transition:.25s;position:relative;overflow:hidden}
.more-btn::before{content:'';position:absolute;inset:0;background:var(--text);transform:translateY(100%);transition:transform .3s ease;z-index:0}
.more-btn:hover::before{transform:translateY(0)}
.more-btn:hover{border-color:var(--text)}
.more-btn span,.more-btn svg{position:relative;z-index:1;transition:color .3s}
.more-btn:hover span,.more-btn:hover svg{color:#fff}
.more-btn svg{transition:transform .2s,color .3s}
.more-btn:hover svg{transform:translateY(2px)}
.post-count{font-size:12px;color:var(--text3);margin-top:12px}

/* ─── MISC ─── */
.no-results{display:none;grid-column:1/-1;padding:80px 40px;text-align:center;background:var(--surface)}
.no-results h3{font-size:17px;font-weight:600;margin-bottom:6px}
.no-results p{font-size:14px;color:var(--text2)}
.hidden{display:none!important}

''' + CSS_FOOTER + '''

/* ─── RESPONSIVE ─── */
@media(max-width:960px){.grid{grid-template-columns:repeat(2,1fr)}.pills{display:none}.search-wrap{display:none}}
@media(max-width:640px){.grid{grid-template-columns:1fr}.nav{padding:0 16px}.container{padding-left:16px;padding-right:16px}.card-body,.card--featured .card-body{padding:20px}.card::before,.card::after,.card-img::after,.card-arrow,.grid-wrap::before,.grid-wrap::after,.z-deco{display:none}.sec-head{padding:24px 0 14px}.footer-in{flex-direction:column;gap:16px;text-align:center}}
</style>
</head>
<body>
<div class="z-bg"></div>
<div class="page">
''' + nav_html("all") + '''
<div class="container" style="padding-top:24px">
  <div id="feat-section">
    <div class="sec-head"><span class="sec-label">Featured</span></div>
    <div class="grid-wrap"><div class="grid" id="feat">%%featured_cards%%</div></div>
  </div>
  <div class="sec-head"><span class="sec-label">Latest</span></div>
  <div class="grid-wrap"><div class="grid" id="grid">
    %%post_cards%%
    <div class="no-results" id="empty"><h3>No posts found</h3><p>Try a different search term or category.</p></div>
  </div></div>
</div>
<div class="more-wrap">
  <button class="more-btn" id="more"><span>Show more</span><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
  <div class="post-count" id="cnt"></div>
</div>
''' + FOOTER_HTML + '''
<script>
(function(){
  const PER=21;let page=1,filter='all',q='';
  const grid=document.getElementById('grid'),featSec=document.getElementById('feat-section');
  const cards=[...grid.querySelectorAll('.card')];
  const btn=document.getElementById('more'),cnt=document.getElementById('cnt');
  const empty=document.getElementById('empty'),input=document.getElementById('q');
  function vis(){
    return cards.filter(c=>{
      const cat=c.dataset.category,t=(c.querySelector('.card-title')||{}).textContent||'';
      const ex=(c.querySelector('.card-excerpt')||{}).textContent||'';
      return(filter==='all'||cat===filter)&&(!q||t.toLowerCase().includes(q)||ex.toLowerCase().includes(q));
    });
  }
  function render(){
    const v=vis(),show=v.slice(0,page*PER);
    cards.forEach(c=>c.classList.add('hidden'));
    show.forEach(c=>c.classList.remove('hidden'));
    const filt=filter!=='all'||q;
    featSec.style.display=filt?'none':'';
    empty.style.display=v.length===0&&filt?'block':'none';
    btn.style.display=show.length<v.length?'':'none';
    cnt.textContent=show.length+' of '+v.length+' posts';
  }
  document.querySelectorAll('.pill[data-f]').forEach(p=>p.addEventListener('click',(e)=>{
    e.preventDefault();
    document.querySelector('.pill.on').classList.remove('on');
    p.classList.add('on');filter=p.dataset.f;page=1;render();
    history.replaceState(null,'',filter==='all'?'/':'/?c='+filter);
  }));
  let t;input.addEventListener('input',e=>{clearTimeout(t);t=setTimeout(()=>{q=e.target.value.trim().toLowerCase();page=1;render();},150);});
  btn.addEventListener('click',()=>{page++;render();});
  // Read ?c= param on load
  const sp=new URLSearchParams(location.search);
  if(sp.get('c')){
    const pill=document.querySelector('.pill[data-f="'+sp.get('c')+'"]');
    if(pill){document.querySelector('.pill.on').classList.remove('on');pill.classList.add('on');filter=sp.get('c');}
  }
  render();
})();
</script>
</div>
</body>
</html>'''

POST_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%%title_raw%% \u2013 Zerion Blog</title>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
<style>
''' + CSS_BASE + '''

/* ─── POST NAV ─── */
.nav{position:sticky;top:0;z-index:100;height:var(--nav-h);display:flex;align-items:center;padding:0 32px;background:rgba(247,247,248,.85);backdrop-filter:saturate(180%) blur(16px);-webkit-backdrop-filter:saturate(180%) blur(16px);border-bottom:1px solid var(--border)}
.nav-in{max-width:var(--max);width:100%;margin:0 auto;display:flex;align-items:center;justify-content:space-between}
.nav-left{display:flex;align-items:center;gap:24px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);flex-shrink:0}
.logo svg{height:22px;width:auto}
.logo-sep{width:1px;height:20px;background:var(--border)}
.logo span{font-size:14px;font-weight:600;color:var(--text2);letter-spacing:-.01em}
.back{display:flex;align-items:center;gap:6px;text-decoration:none;color:var(--text3);font-size:13px;font-weight:500;transition:color .15s}
.back:hover{color:var(--text)}
.back svg{flex-shrink:0}
.share-btn{padding:7px 14px;border-radius:var(--rs);border:1.5px solid var(--border);background:var(--surface);font:13px/1 var(--font);font-weight:500;color:var(--text2);cursor:pointer;display:flex;align-items:center;gap:6px;transition:.2s}
.share-btn:hover{color:var(--text);border-color:var(--text3);background:var(--hover)}

/* ─── PROGRESS BAR ─── */
.progress{position:fixed;top:60px;left:0;height:2px;background:linear-gradient(90deg,var(--accent),#6c8cff);width:0;z-index:99;transition:width .15s;box-shadow:0 0 8px rgba(41,98,239,.3)}

/* ─── ARTICLE HEADER ─── */
.article-head{max-width:720px;margin:0 auto;padding:64px 24px 0;text-align:center;position:relative}

/* Decorative crosshair above article */
.article-head::before{content:'+';position:absolute;top:24px;right:0;font-size:14px;font-weight:300;color:var(--text3);opacity:.3}

.article-tag{display:inline-block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);margin-bottom:20px;padding:5px 14px;background:var(--accent-light);border-radius:999px;border:1px solid rgba(41,98,239,.12)}
.article-h1{font-size:42px;font-weight:700;line-height:1.1;letter-spacing:-.04em;margin-bottom:28px}
.article-authors{display:flex;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap;margin-bottom:14px}
.author{display:flex;align-items:center;gap:8px}
.author-link{display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;transition:opacity .15s}
.author-link:hover{opacity:.7}
.author-avatar{width:34px;height:34px;border-radius:50%;object-fit:cover;background:#e5e5e5;border:2px solid var(--surface);box-shadow:0 0 0 1px var(--border)}
.author-avatar-placeholder{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#6c8cff);border:2px solid var(--surface);box-shadow:0 0 0 1px var(--border)}
.author-name{font-size:14px;font-weight:500}
.article-dateline{font-size:13px;color:var(--text3);margin-bottom:44px;display:flex;align-items:center;justify-content:center;gap:8px}
.article-dateline::before,.article-dateline::after{content:'';width:24px;height:1px;background:var(--border)}

/* ─── HERO IMAGE ─── */
.hero-wrap{position:relative;max-width:960px;margin:0 auto 56px}
.hero-image{display:block;width:100%;border-radius:var(--r);box-shadow:0 4px 32px rgba(0,0,0,.08);border:1px solid var(--border)}

/* Dashed outline offset around hero image */
.hero-wrap::before{content:'';position:absolute;inset:-8px;border:1.5px dashed var(--border-dashed);border-radius:calc(var(--r) + 4px);pointer-events:none}
/* Corner + mark */
.hero-wrap::after{content:'+';position:absolute;top:-14px;right:-14px;font-size:13px;font-weight:300;color:var(--text3);opacity:.4}

/* ─── CONTENT ─── */
.content{max-width:720px;margin:0 auto;padding:0 24px 80px}
.content p{font-size:17px;line-height:1.78;color:var(--text2);margin-bottom:24px}
.content h2{font-size:26px;font-weight:700;letter-spacing:-.025em;margin:56px 0 16px;color:var(--text);position:relative;padding-top:32px}
.content h2::before{content:'';position:absolute;top:0;left:0;width:32px;height:2px;background:var(--accent);border-radius:1px}
.content h3{font-size:20px;font-weight:600;letter-spacing:-.01em;margin:40px 0 12px;color:var(--text)}
.content h4{font-size:17px;font-weight:600;margin:28px 0 8px}
.content img{max-width:100%;height:auto;border-radius:var(--rs);margin:28px 0;border:1px solid var(--border)}
.content a{color:var(--accent);text-decoration:none;font-weight:500;transition:color .15s;border-bottom:1px solid transparent}
.content a:hover{border-bottom-color:var(--accent)}
.content ul,.content ol{margin:0 0 24px 24px;font-size:17px;line-height:1.78;color:var(--text2)}
.content li{margin-bottom:8px}
.content li::marker{color:var(--accent)}
.content blockquote{border-left:3px solid var(--accent);padding:20px 28px;margin:32px 0;color:var(--text2);background:var(--accent-light);border-radius:0 var(--rs) var(--rs) 0;font-style:italic}
.content pre{background:#0f0f1a;color:#e0e0e0;padding:24px 28px;border-radius:12px;overflow-x:auto;margin:28px 0;font-size:14px;line-height:1.65;border:1px solid rgba(255,255,255,.06)}
.content code{font-family:'SF Mono','Fira Code','JetBrains Mono',monospace;font-size:.87em}
.content p code{background:rgba(0,0,0,.05);padding:2px 8px;border-radius:5px;font-size:.85em}
.content figure{margin:36px 0}
.content figcaption{text-align:center;font-size:12px;color:var(--text3);margin-top:10px;font-style:italic}
.content .kg-image-card img,.content .kg-gallery-image img{max-width:100%;border-radius:var(--rs);border:1px solid var(--border)}
.content .kg-embed-card{margin:28px 0}
.content .kg-embed-card iframe{max-width:100%;border-radius:var(--rs)}
.content .kg-bookmark-card{border:1.5px solid var(--border);border-radius:var(--rs);overflow:hidden;margin:28px 0;transition:border-color .2s}
.content .kg-bookmark-card:hover{border-color:var(--accent)}
.content .kg-bookmark-container{display:flex;text-decoration:none;color:inherit}
.content .kg-bookmark-content{padding:20px;flex:1}
.content .kg-bookmark-title{font-weight:600;font-size:15px}
.content .kg-bookmark-description{font-size:13px;color:var(--text2);margin-top:6px}
.content hr{border:none;height:1px;background:var(--border);margin:56px 0;position:relative}
.content hr::after{content:'';position:absolute;left:50%;top:-3px;width:6px;height:6px;background:var(--bg);border:1.5px solid var(--border);border-radius:50%;transform:translateX(-50%)}

/* ─── TAGS ─── */
.post-tags{display:flex;flex-wrap:wrap;gap:8px;padding-top:36px;border-top:1px dashed var(--border-dashed);margin-top:56px}
.tag-pill{padding:6px 16px;border-radius:999px;border:1.5px solid var(--border);font-size:12px;font-weight:500;color:var(--text2);transition:all .2s}
.tag-pill:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}

''' + CSS_FOOTER + '''

@media(max-width:640px){.article-h1{font-size:28px}.article-head{padding-top:40px}.article-head::before{display:none}.content h2{font-size:22px;padding-top:24px}.content h2::before{width:24px}.hero-wrap::before,.hero-wrap::after{display:none}.nav{padding:0 16px}.footer-in{flex-direction:column;gap:16px;text-align:center}}
</style>
</head>
<body>
<div class="z-bg"></div>
<div class="page">
<nav class="nav">
<div class="nav-in">
  <div class="nav-left">
    <a href="/" class="logo">%%logo%%<div class="logo-sep"></div><span>Blog</span></a>
    <a href="/" class="back"><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M10 12L6 8l4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>All posts</a>
  </div>
  <button class="share-btn" onclick="navigator.clipboard.writeText(location.href).then(()=>{this.innerHTML='Copied!';setTimeout(()=>this.innerHTML='<svg width=\\'13\\' height=\\'13\\' viewBox=\\'0 0 16 16\\' fill=\\'none\\'><path d=\\'M4 12h8M8 2v8M5 5l3-3 3 3\\' stroke=\\'currentColor\\' stroke-width=\\'1.5\\' stroke-linecap=\\'round\\' stroke-linejoin=\\'round\\'/></svg>Share',1500)})">
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M4 12h8M8 2v8M5 5l3-3 3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Share
  </button>
</div>
</nav>
<div class="progress" id="prog"></div>
<article>
<header class="article-head">
  <span class="article-tag">%%primary_tag%%</span>
  <h1 class="article-h1">%%title%%</h1>
  <div class="article-authors">%%authors%%</div>
  <div class="article-dateline">%%date%% &middot; %%reading_time%%</div>
  %%hero_image%%
</header>
<div class="content">%%content%%%%tags%%</div>
</article>
''' + FOOTER_HTML + '''
<script>
window.addEventListener('scroll',()=>{
  const h=document.documentElement;
  const pct=h.scrollTop/(h.scrollHeight-h.clientHeight)*100;
  document.getElementById('prog').style.width=pct+'%';
});
</script>
</div>
</body>
</html>'''

CHANGELOG_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Changelog \u2013 Zerion Blog</title>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
<style>
''' + CSS_BASE + CSS_NAV + '''
.hero{max-width:860px;margin:56px auto 0;padding:0 32px}
.hero h1{font-size:44px;font-weight:700;letter-spacing:-.04em;line-height:1.08;margin-bottom:12px}
.hero p{font-size:17px;color:var(--text2);max-width:540px;line-height:1.6}
.timeline{max-width:860px;margin:48px auto 80px;padding:0 32px;position:relative}
.timeline::before{content:'';position:absolute;top:0;bottom:0;left:calc(32px + 120px + 16px);width:0;border-left:1px dashed var(--border)}
.cl-entry{display:grid;grid-template-columns:120px 32px 1fr;gap:0;padding-bottom:52px;position:relative}
.cl-entry:last-child{padding-bottom:0}
.cl-date-col{padding-top:4px;text-align:right;position:sticky;top:76px;align-self:start}
.cl-date{font-size:13px;font-weight:500;color:var(--text3);white-space:nowrap}
.cl-line-col{display:flex;flex-direction:column;align-items:center;position:relative}
.cl-dot{width:9px;height:9px;border-radius:50%;background:var(--accent);margin-top:7px;flex-shrink:0;position:relative;z-index:1;box-shadow:0 0 0 3px var(--accent-light)}
.cl-content{padding-left:4px}
.cl-img{display:block;border-radius:var(--r);overflow:hidden;margin-bottom:16px;background:linear-gradient(135deg,#f0f0f2,#e8e8ec);aspect-ratio:2/1;border:1px solid var(--border);position:relative}
.cl-img::after{content:'';position:absolute;inset:0;border-radius:var(--r);border:1px dashed transparent;transition:border-color .3s;pointer-events:none}
.cl-img:hover::after{border-color:var(--accent)}
.cl-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s cubic-bezier(.25,.46,.45,.94)}
.cl-img:hover img{transform:scale(1.03)}
.cl-title{display:block;font-size:20px;font-weight:600;letter-spacing:-.02em;line-height:1.3;color:var(--text);text-decoration:none;margin-bottom:8px;transition:color .2s}
.cl-title:hover{color:var(--accent)}
.cl-excerpt{font-size:15px;line-height:1.6;color:var(--text2);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
''' + CSS_FOOTER + '''
@media(max-width:960px){.pills{display:none}.search-wrap{display:none}}
@media(max-width:640px){.cl-entry{grid-template-columns:1fr}.cl-date-col{text-align:left;padding:0 0 4px;position:static}.cl-line-col{display:none}.timeline::before{display:none}.cl-content{padding-left:0}.hero h1{font-size:28px}.hero,.timeline{padding:0 16px}.nav{padding:0 16px}.footer-in{flex-direction:column;gap:16px;text-align:center}}
</style>
</head>
<body>
<div class="z-bg"></div>
<div class="page">
''' + nav_html("changelog") + '''
<div class="hero">
  <h1>Changelog</h1>
  <p>What\u2019s new in the Zerion wallet \u2013 product updates, new chains, and feature releases.</p>
</div>
<div class="timeline">%%entries%%</div>
''' + FOOTER_HTML + '''
</div>
</body>
</html>'''


# ────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────

def main():
    print("Loading content...")
    posts = load_posts()
    pages = load_pages()
    authors = load_authors()
    print(f"  {len(posts)} posts, {len(pages)} pages, {len(authors)} authors")

    # Prepare output dir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Copy favicon
    favicon_src = ROOT / "favicon.png"
    if favicon_src.exists():
        shutil.copy2(favicon_src, OUTPUT_DIR / "favicon.png")

    # Index
    print("Generating index.html...")
    (OUTPUT_DIR / "index.html").write_text(generate_index(posts))

    # Posts: /{slug}/index.html
    print(f"Generating {len(posts)} post pages...")
    for i, post in enumerate(posts):
        d = OUTPUT_DIR / post["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(generate_post_html(post))
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(posts)}")

    # Author pages
    print("Generating author pages...")
    posts_by_author = {}
    for p in posts:
        for a in p["authors"]:
            slug = a.get("slug")
            if slug:
                posts_by_author.setdefault(slug, []).append(p)

    author_count = 0
    for slug, author_posts in posts_by_author.items():
        author_info = authors.get(slug, {"name": slug, "slug": slug, "bio": "", "profile_image": ""})
        d = OUTPUT_DIR / "author" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(generate_author_page(author_info, author_posts))
        author_count += 1
    print(f"  {author_count} author pages")

    # Tag pages
    print("Generating tag pages...")
    posts_by_tag = {}
    for p in posts:
        for t in p["tags"]:
            name = t["name"]
            slug = t["slug"]
            posts_by_tag.setdefault((name, slug), []).append(p)

    tag_count = 0
    for (name, slug), tag_posts in posts_by_tag.items():
        d = OUTPUT_DIR / "tag" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(generate_tag_page(name, tag_posts))
        tag_count += 1
    print(f"  {tag_count} tag pages")

    # Static pages
    print("Generating static pages...")
    for page in pages:
        d = OUTPUT_DIR / page["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(generate_static_page(page))
    print(f"  {len(pages)} static pages")

    # Changelog
    print("Generating changelog...")
    changelog_tags = {"Zerion Wallet", "product updates"}
    changelog_posts = [p for p in posts if any(t["name"] in changelog_tags for t in p["tags"])]
    d = OUTPUT_DIR / "changelog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(generate_changelog(changelog_posts))
    print(f"  {len(changelog_posts)} changelog entries")

    total = len(posts) + author_count + tag_count + len(pages) + 1
    print(f"\nDone! {total} pages generated in public/")

    if "--serve" in sys.argv:
        os.chdir(OUTPUT_DIR)
        import http.server
        print(f"\nServing at http://localhost:3000")
        http.server.HTTPServer(("", 3000), http.server.SimpleHTTPRequestHandler).serve_forever()


if __name__ == "__main__":
    main()
