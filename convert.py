#!/usr/bin/env python3
"""One-time: convert Ghost JSON export to markdown files with frontmatter."""

import json
import re
import os
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).parent / "data.json"
CONTENT_DIR = Path(__file__).parent / "content" / "posts"
PAGES_DIR = Path(__file__).parent / "content" / "pages"
GHOST_URL = "https://zerion.io/blog"


def html_to_markdown(html_str):
    """Lightweight HTML-to-markdown. Keeps HTML that markdown can't express."""
    if not html_str:
        return ""
    text = html_str
    # Fix Ghost URL placeholders
    text = text.replace("__GHOST_URL__", GHOST_URL)
    return text.strip()


def slugify_date(iso_str):
    """Extract YYYY-MM-DD from ISO date."""
    if not iso_str:
        return "0000-00-00"
    return iso_str[:10]


def escape_yaml(s):
    """Escape a string for YAML frontmatter."""
    if not s:
        return ""
    # Quote if it contains special chars
    if any(c in s for c in [':', '"', "'", '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`']):
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s


def get_excerpt(plaintext, max_len=200):
    if not plaintext:
        return ""
    text = plaintext.strip().replace("\n", " ")
    if len(text) > max_len:
        return text[:max_len].rsplit(" ", 1)[0] + "\u2026"
    return text


def main():
    with open(DATA) as f:
        raw = json.load(f)
    data = raw["db"][0]["data"]

    users = {u["id"]: u for u in data["users"]}
    tags = {t["id"]: t for t in data["tags"]}

    # Build lookups
    post_authors = {}
    for pa in data["posts_authors"]:
        post_authors.setdefault(pa["post_id"], []).append(users.get(pa["author_id"]))

    post_tags = {}
    for pt in data["posts_tags"]:
        tag = tags.get(pt["tag_id"])
        if tag and tag["visibility"] == "public":
            post_tags.setdefault(pt["post_id"], []).append(tag)

    # Process posts and pages
    for p in data["posts"]:
        if p["status"] != "published":
            continue

        is_page = p["type"] == "page"
        out_dir = PAGES_DIR if is_page else CONTENT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        slug = p["slug"]
        title = p["title"] or "Untitled"
        published_at = p.get("published_at", "")
        date_str = slugify_date(published_at)
        feature_image = (p.get("feature_image") or "").replace("__GHOST_URL__", GHOST_URL)
        featured = p.get("featured", 0)

        # Authors
        authors_list = [a for a in post_authors.get(p["id"], []) if a]
        author_names = [a["name"] for a in authors_list]
        author_slugs = [a["slug"] for a in authors_list]

        # Tags
        tags_list = post_tags.get(p["id"], [])
        tag_names = [t["name"] for t in tags_list if not t["name"].startswith("#")]

        # Excerpt
        excerpt = get_excerpt(p.get("plaintext"))

        # HTML content
        content_html = html_to_markdown(p.get("html", ""))

        # Build frontmatter
        fm_lines = [
            "---",
            f"title: {escape_yaml(title)}",
            f"slug: {slug}",
            f"date: {date_str}",
        ]
        if published_at:
            fm_lines.append(f"published_at: {published_at}")
        if feature_image:
            fm_lines.append(f"feature_image: {feature_image}")
        if featured:
            fm_lines.append(f"featured: true")
        if author_names:
            fm_lines.append(f"authors:")
            for i, name in enumerate(author_names):
                fm_lines.append(f"  - name: {escape_yaml(name)}")
                fm_lines.append(f"    slug: {author_slugs[i]}")
                profile_img = (authors_list[i].get("profile_image") or "").replace("__GHOST_URL__", GHOST_URL)
                if profile_img:
                    fm_lines.append(f"    avatar: {profile_img}")
        if tag_names:
            fm_lines.append(f"tags:")
            for t in tag_names:
                fm_lines.append(f"  - {escape_yaml(t)}")
        if excerpt:
            fm_lines.append(f"excerpt: {escape_yaml(excerpt)}")

        fm_lines.append("---")

        # File name: date-slug.md for posts, slug.md for pages
        if is_page:
            filename = f"{slug}.md"
        else:
            filename = f"{date_str}-{slug}.md"

        file_path = out_dir / filename
        file_path.write_text("\n".join(fm_lines) + "\n\n" + content_html + "\n")

    # Count results
    post_count = len(list(CONTENT_DIR.glob("*.md")))
    page_count = len(list(PAGES_DIR.glob("*.md")))
    print(f"Converted {post_count} posts to content/posts/")
    print(f"Converted {page_count} pages to content/pages/")

    # Write authors.json for the build script
    authors_out = {}
    for uid, u in users.items():
        authors_out[u["slug"]] = {
            "name": u["name"],
            "slug": u["slug"],
            "bio": u.get("bio") or "",
            "profile_image": (u.get("profile_image") or "").replace("__GHOST_URL__", GHOST_URL),
        }
    authors_path = Path(__file__).parent / "content" / "authors.json"
    with open(authors_path, "w") as f:
        json.dump(authors_out, f, indent=2)
    print(f"Wrote {len(authors_out)} authors to content/authors.json")


if __name__ == "__main__":
    main()
