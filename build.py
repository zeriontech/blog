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
                excerpt = plain[:180].rsplit(" ", 1)[0] + "\u2026"
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
        hero_img = f'<img src="{html.escape(post["feature_image"])}" alt="" class="hero-image">'

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
        max_lines = 3 if featured else 2
        excerpt = f'<p class="card-excerpt" style="-webkit-line-clamp:{max_lines}">{html.escape(post["excerpt"])}</p>'

    return f'''<a href="/{html.escape(post["slug"])}/" class="{cls}" data-category="{post["category"]}">
{img}<div class="card-body">{tag}<h2 class="card-title">{html.escape(post["title"])}</h2>{excerpt}<div class="card-meta"><span>{html.escape(author_name)}</span><span class="sep">&middot;</span><time>{post["date_display"]}</time></div></div></a>'''


def generate_index(posts):
    featured = [p for p in posts if p["feature_image"]][:3]
    if len(featured) < 3:
        featured = posts[:3]
    remaining = [p for p in posts if p not in featured]
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
        '<div class="hero">\n  <h1>Zerion Blog</h1>\n  <p>Product updates, developer guides, and insights from the team building the crypto wallet and onchain data API.</p>\n</div>',
        f'<div class="hero">{avatar}<h1>{name}</h1><p>{bio}</p></div>',
    ).replace(
        '<div class="sec-head"><span class="sec-label">Featured</span><div class="sec-line"></div></div>\n  <div class="grid" id="feat"></div>',
        '',
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
        '<div class="hero">\n  <h1>Zerion Blog</h1>\n  <p>Product updates, developer guides, and insights from the team building the crypto wallet and onchain data API.</p>\n</div>',
        f'<div class="hero"><h1>{name}</h1><p>Posts tagged with {name}</p></div>',
    ).replace(
        '<div class="sec-head"><span class="sec-label">Featured</span><div class="sec-line"></div></div>\n  <div class="grid" id="feat"></div>',
        '',
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
  --accent:#2962EF;--border:rgba(0,0,0,.07);--hover:rgba(0,0,0,.025);
  --r:14px;--rs:8px;--max:1240px;--nav-h:60px;
  --font:'Inter',ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}'''

CSS_BASE = '''
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
''' + CSS_VARS + '''
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;line-height:1.5}
'''

CSS_NAV = '''
.nav{position:sticky;top:0;z-index:100;height:var(--nav-h);display:flex;align-items:center;padding:0 32px;background:rgba(247,247,248,.85);backdrop-filter:saturate(180%) blur(16px);-webkit-backdrop-filter:saturate(180%) blur(16px);border-bottom:1px solid var(--border)}
.nav-in{max-width:var(--max);width:100%;margin:0 auto;display:flex;align-items:center;gap:32px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);flex-shrink:0}
.logo svg{height:22px;width:auto}
.logo-sep{width:1px;height:20px;background:var(--border)}
.logo span{font-size:14px;font-weight:600;color:var(--text2);letter-spacing:-.01em}
.pills{display:flex;gap:2px;flex:1;justify-content:center;overflow-x:auto;scrollbar-width:none}
.pills::-webkit-scrollbar{display:none}
.pill{padding:7px 14px;border-radius:999px;font-size:13px;font-weight:500;border:none;background:0;color:var(--text2);cursor:pointer;transition:.15s;white-space:nowrap;font-family:inherit;text-decoration:none;display:inline-flex;align-items:center}
.pill:hover{color:var(--text);background:rgba(0,0,0,.04)}
.pill.on{background:var(--text);color:#fff}
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
</footer>'''

NAV_PILLS_HTML = '''<nav class="nav">
<div class="nav-in">
  <a href="/" class="logo">
    %%logo%%
    <div class="logo-sep"></div>
    <span>Blog</span>
  </a>
  <div class="pills">
    <button class="pill{all_active}" data-f="all">All Posts</button>
    <button class="pill{wallet_active}" data-f="zerion-wallet">Wallet</button>
    <button class="pill{api_active}" data-f="zerion-api">API</button>
    <button class="pill{learn_active}" data-f="learn">Learn</button>
    <button class="pill{defi_active}" data-f="defi">DeFi</button>
    <a href="/changelog/" class="pill{changelog_active}" style="text-decoration:none">Changelog</a>
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
.hero{{max-width:var(--max);margin:48px auto 0;padding:0 32px}}
.hero h1{{font-size:40px;font-weight:700;letter-spacing:-.035em;line-height:1.1;margin-bottom:8px}}
.hero p{{font-size:17px;color:var(--text2);max-width:540px;line-height:1.55}}
.container{{max-width:var(--max);margin:0 auto;padding:0 32px}}
.sec-head{{display:flex;align-items:center;gap:12px;padding:40px 0 20px}}
.sec-label{{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--text3)}}
.sec-line{{flex:1;height:1px;background:var(--border)}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border-radius:var(--r);overflow:hidden}}
.card{{display:flex;flex-direction:column;background:var(--surface);text-decoration:none;color:inherit;transition:background .2s}}
.card:hover{{background:var(--hover)}}
.card-img{{aspect-ratio:16/9;overflow:hidden;background:#eee}}
.card-img img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s cubic-bezier(.25,.46,.45,.94)}}
.card:hover .card-img img{{transform:scale(1.03)}}
.card-body{{padding:28px 28px 24px;display:flex;flex-direction:column;flex:1}}
.card--featured .card-body{{padding:32px 32px 28px}}
.card-tag{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);margin-bottom:10px}}
.card-title{{font-size:17px;font-weight:600;line-height:1.35;letter-spacing:-.015em;margin-bottom:8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.card--featured .card-title{{font-size:22px;letter-spacing:-.02em;-webkit-line-clamp:3}}
.card-excerpt{{font-size:14px;line-height:1.55;color:var(--text2);margin-bottom:auto;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden;padding-bottom:16px}}
.card-meta{{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text3);margin-top:auto;padding-top:16px;border-top:1px solid var(--border)}}
.card-meta .sep{{opacity:.4}}
.more-wrap{{padding:48px 0 80px;text-align:center}}
.more-btn{{display:inline-flex;align-items:center;gap:8px;padding:10px 24px;border-radius:999px;border:1.5px solid var(--border);background:var(--surface);font:14px/1.2 var(--font);font-weight:500;color:var(--text);cursor:pointer;transition:.2s}}
.more-btn:hover{{background:var(--text);color:#fff;border-color:var(--text)}}
.more-btn svg{{transition:transform .2s}}
.more-btn:hover svg{{transform:translateY(2px)}}
.post-count{{font-size:12px;color:var(--text3);margin-top:10px}}
.no-results{{display:none;grid-column:1/-1;padding:80px 40px;text-align:center;background:var(--surface)}}
.no-results h3{{font-size:17px;font-weight:600;margin-bottom:6px}}
.no-results p{{font-size:14px;color:var(--text2)}}
.hidden{{display:none!important}}
''' + CSS_FOOTER + '''
@media(max-width:960px){{.grid{{grid-template-columns:repeat(2,1fr)}}.pills{{display:none}}.search-wrap{{display:none}}}}
@media(max-width:640px){{.grid{{grid-template-columns:1fr}}.nav{{padding:0 16px}}.hero,.container{{padding:0 16px}}.hero{{margin-top:32px}}.hero h1{{font-size:28px}}.card-body,.card--featured .card-body{{padding:20px}}.sec-head{{padding:32px 0 16px}}.footer-in{{flex-direction:column;gap:16px;text-align:center}}}}
</style>
</head>
<body>
''' + nav_html("all") + '''
<div class="hero">
  <h1>Zerion Blog</h1>
  <p>Product updates, developer guides, and insights from the team building the crypto wallet and onchain data API.</p>
</div>
<div class="container">
  <div class="sec-head"><span class="sec-label">Featured</span><div class="sec-line"></div></div>
  <div class="grid" id="feat">%%featured_cards%%</div>
  <div class="sec-head"><span class="sec-label">Latest</span><div class="sec-line"></div></div>
  <div class="grid" id="grid">
    %%post_cards%%
    <div class="no-results" id="empty"><h3>No posts found</h3><p>Try a different search term or category.</p></div>
  </div>
</div>
<div class="more-wrap">
  <button class="more-btn" id="more">Show more<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
  <div class="post-count" id="cnt"></div>
</div>
''' + FOOTER_HTML + '''
<script>
(function(){{
  const PER=21;let page=1,filter='all',q='';
  const grid=document.getElementById('grid'),feat=document.getElementById('feat');
  const cards=[...grid.querySelectorAll('.card')];
  const btn=document.getElementById('more'),cnt=document.getElementById('cnt');
  const empty=document.getElementById('empty'),input=document.getElementById('q');
  function vis(){{
    return cards.filter(c=>{{
      const cat=c.dataset.category,t=(c.querySelector('.card-title')||{{}}).textContent||'';
      const ex=(c.querySelector('.card-excerpt')||{{}}).textContent||'';
      return(filter==='all'||cat===filter)&&(!q||t.toLowerCase().includes(q)||ex.toLowerCase().includes(q));
    }});
  }}
  function render(){{
    const v=vis(),show=v.slice(0,page*PER);
    cards.forEach(c=>c.classList.add('hidden'));
    show.forEach(c=>c.classList.remove('hidden'));
    const filt=filter!=='all'||q;
    feat.style.display=filt?'none':'';
    feat.previousElementSibling.style.display=filt?'none':'';
    empty.style.display=v.length===0&&filt?'block':'none';
    btn.style.display=show.length<v.length?'':'none';
    cnt.textContent=show.length+' of '+v.length+' posts';
  }}
  document.querySelectorAll('.pill[data-f]').forEach(p=>p.addEventListener('click',()=>{{
    document.querySelector('.pill.on').classList.remove('on');
    p.classList.add('on');filter=p.dataset.f;page=1;render();
  }}));
  let t;input.addEventListener('input',e=>{{clearTimeout(t);t=setTimeout(()=>{{q=e.target.value.trim().toLowerCase();page=1;render();}},150);}});
  btn.addEventListener('click',()=>{{page++;render();}});
  render();
}})();
</script>
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
.nav{{position:sticky;top:0;z-index:100;height:var(--nav-h);display:flex;align-items:center;padding:0 32px;background:rgba(247,247,248,.85);backdrop-filter:saturate(180%) blur(16px);-webkit-backdrop-filter:saturate(180%) blur(16px);border-bottom:1px solid var(--border)}}
.nav-in{{max-width:var(--max);width:100%;margin:0 auto;display:flex;align-items:center;justify-content:space-between}}
.nav-left{{display:flex;align-items:center;gap:24px}}
.logo{{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);flex-shrink:0}}
.logo svg{{height:22px;width:auto}}
.logo-sep{{width:1px;height:20px;background:var(--border)}}
.logo span{{font-size:14px;font-weight:600;color:var(--text2);letter-spacing:-.01em}}
.back{{display:flex;align-items:center;gap:6px;text-decoration:none;color:var(--text3);font-size:13px;font-weight:500;transition:color .15s}}
.back:hover{{color:var(--text)}}
.back svg{{flex-shrink:0}}
.share-btn{{padding:7px 14px;border-radius:var(--rs);border:1.5px solid var(--border);background:var(--surface);font:13px/1 var(--font);font-weight:500;color:var(--text2);cursor:pointer;display:flex;align-items:center;gap:6px;transition:.15s}}
.share-btn:hover{{color:var(--text);border-color:var(--text3)}}
.progress{{position:fixed;top:60px;left:0;height:2px;background:var(--accent);width:0;z-index:99;transition:width .1s}}
.article-head{{max-width:720px;margin:0 auto;padding:56px 24px 0;text-align:center}}
.article-tag{{display:inline-block;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);margin-bottom:16px;padding:4px 12px;background:rgba(41,98,239,.06);border-radius:999px}}
.article-h1{{font-size:40px;font-weight:700;line-height:1.12;letter-spacing:-.035em;margin-bottom:24px}}
.article-authors{{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}}
.author{{display:flex;align-items:center;gap:8px}}
.author-link{{display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;transition:opacity .15s}}
.author-link:hover{{opacity:.7}}
.author-avatar{{width:32px;height:32px;border-radius:50%;object-fit:cover;background:#e5e5e5}}
.author-avatar-placeholder{{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#6c8cff)}}
.author-name{{font-size:14px;font-weight:500}}
.article-dateline{{font-size:13px;color:var(--text3);margin-bottom:40px}}
.hero-image{{display:block;max-width:960px;width:100%;margin:0 auto 48px;border-radius:var(--r);box-shadow:0 2px 20px rgba(0,0,0,.06)}}
.content{{max-width:720px;margin:0 auto;padding:0 24px 80px}}
.content p{{font-size:17px;line-height:1.75;color:var(--text2);margin-bottom:24px}}
.content h2{{font-size:26px;font-weight:700;letter-spacing:-.02em;margin:48px 0 16px;color:var(--text)}}
.content h3{{font-size:20px;font-weight:600;letter-spacing:-.01em;margin:36px 0 12px;color:var(--text)}}
.content h4{{font-size:17px;font-weight:600;margin:28px 0 8px}}
.content img{{max-width:100%;height:auto;border-radius:var(--rs);margin:24px 0}}
.content a{{color:var(--accent);text-decoration:none;font-weight:500;transition:opacity .15s}}
.content a:hover{{opacity:.75}}
.content ul,.content ol{{margin:0 0 24px 24px;font-size:17px;line-height:1.75;color:var(--text2)}}
.content li{{margin-bottom:8px}}
.content blockquote{{border-left:3px solid var(--accent);padding:16px 24px;margin:28px 0;color:var(--text2);background:rgba(41,98,239,.03);border-radius:0 var(--rs) var(--rs) 0}}
.content pre{{background:#1a1a2e;color:#e0e0e0;padding:20px 24px;border-radius:10px;overflow-x:auto;margin:24px 0;font-size:14px;line-height:1.6}}
.content code{{font-family:'SF Mono','Fira Code','JetBrains Mono',monospace;font-size:.88em}}
.content p code{{background:rgba(0,0,0,.05);padding:2px 7px;border-radius:4px}}
.content figure{{margin:32px 0}}
.content figcaption{{text-align:center;font-size:13px;color:var(--text3);margin-top:8px}}
.content .kg-image-card img,.content .kg-gallery-image img{{max-width:100%;border-radius:var(--rs)}}
.content .kg-embed-card{{margin:24px 0}}
.content .kg-embed-card iframe{{max-width:100%;border-radius:var(--rs)}}
.content .kg-bookmark-card{{border:1.5px solid var(--border);border-radius:var(--rs);overflow:hidden;margin:24px 0}}
.content .kg-bookmark-container{{display:flex;text-decoration:none;color:inherit}}
.content .kg-bookmark-content{{padding:16px;flex:1}}
.content .kg-bookmark-title{{font-weight:600;font-size:15px}}
.content .kg-bookmark-description{{font-size:13px;color:var(--text2);margin-top:4px}}
.content hr{{border:none;height:1px;background:var(--border);margin:48px 0}}
.post-tags{{display:flex;flex-wrap:wrap;gap:8px;padding-top:32px;border-top:1px solid var(--border);margin-top:48px}}
.tag-pill{{padding:5px 14px;border-radius:999px;border:1.5px solid var(--border);font-size:12px;font-weight:500;color:var(--text2)}}
''' + CSS_FOOTER + '''
@media(max-width:640px){{.article-h1{{font-size:28px}}.article-head{{padding-top:36px}}.content h2{{font-size:22px}}.nav{{padding:0 16px}}.footer-in{{flex-direction:column;gap:16px;text-align:center}}}}
</style>
</head>
<body>
<nav class="nav">
<div class="nav-in">
  <div class="nav-left">
    <a href="/" class="logo">%%logo%%<div class="logo-sep"></div><span>Blog</span></a>
    <a href="/" class="back"><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M10 12L6 8l4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>All posts</a>
  </div>
  <button class="share-btn" onclick="navigator.clipboard.writeText(location.href).then(()=>{{this.innerHTML='Copied!';setTimeout(()=>this.innerHTML='<svg width=\\'13\\' height=\\'13\\' viewBox=\\'0 0 16 16\\' fill=\\'none\\'><path d=\\'M4 12h8M8 2v8M5 5l3-3 3 3\\' stroke=\\'currentColor\\' stroke-width=\\'1.5\\' stroke-linecap=\\'round\\' stroke-linejoin=\\'round\\'/></svg>Share',1500)}})">
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
window.addEventListener('scroll',()=>{{
  const h=document.documentElement;
  const pct=h.scrollTop/(h.scrollHeight-h.clientHeight)*100;
  document.getElementById('prog').style.width=pct+'%';
}});
</script>
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
.hero{{max-width:860px;margin:48px auto 0;padding:0 32px}}
.hero h1{{font-size:40px;font-weight:700;letter-spacing:-.035em;line-height:1.1;margin-bottom:8px}}
.hero p{{font-size:17px;color:var(--text2);max-width:540px;line-height:1.55}}
.timeline{{max-width:860px;margin:48px auto 80px;padding:0 32px}}
.cl-entry{{display:grid;grid-template-columns:120px 32px 1fr;gap:0;padding-bottom:48px;position:relative}}
.cl-entry:last-child{{padding-bottom:0}}
.cl-date-col{{padding-top:4px;text-align:right}}
.cl-date{{font-size:13px;font-weight:500;color:var(--text3);white-space:nowrap}}
.cl-line-col{{display:flex;flex-direction:column;align-items:center;position:relative}}
.cl-dot{{width:9px;height:9px;border-radius:50%;background:var(--accent);margin-top:7px;flex-shrink:0;position:relative;z-index:1}}
.cl-line-col::after{{content:'';position:absolute;top:22px;bottom:0;width:1px;background:var(--border)}}
.cl-entry:last-child .cl-line-col::after{{display:none}}
.cl-content{{padding-left:4px}}
.cl-img{{display:block;border-radius:var(--r);overflow:hidden;margin-bottom:16px;background:#eee;aspect-ratio:2/1}}
.cl-img img{{width:100%;height:100%;object-fit:cover;display:block;transition:opacity .2s}}
.cl-img:hover img{{opacity:.9}}
.cl-title{{display:block;font-size:20px;font-weight:600;letter-spacing:-.02em;line-height:1.3;color:var(--text);text-decoration:none;margin-bottom:8px;transition:color .15s}}
.cl-title:hover{{color:var(--accent)}}
.cl-excerpt{{font-size:15px;line-height:1.6;color:var(--text2);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
''' + CSS_FOOTER + '''
@media(max-width:960px){{.pills{{display:none}}.search-wrap{{display:none}}}}
@media(max-width:640px){{.cl-entry{{grid-template-columns:1fr}}.cl-date-col{{text-align:left;padding:0 0 4px}}.cl-line-col{{display:none}}.cl-content{{padding-left:0}}.hero h1{{font-size:28px}}.hero,.timeline{{padding:0 16px}}.nav{{padding:0 16px}}.footer-in{{flex-direction:column;gap:16px;text-align:center}}}}
</style>
</head>
<body>
''' + nav_html("changelog") + '''
<div class="hero">
  <h1>Changelog</h1>
  <p>What\u2019s new in the Zerion wallet \u2013 product updates, new chains, and feature releases.</p>
</div>
<div class="timeline">%%entries%%</div>
''' + FOOTER_HTML + '''
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
