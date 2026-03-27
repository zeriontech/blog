# Zerion Blog

Self-hosted static blog. Posts are markdown files with YAML frontmatter. A single Python script generates the full site -- no frameworks, no dependencies.

## Structure

```
├── build.py              # Static site generator (Python 3, zero deps)
├── favicon.png           # Site favicon
├── content/
│   ├── posts/            # Blog posts (markdown + HTML body)
│   │   ├── 2026-03-25-new-zerion-api-docs.md
│   │   ├── 2026-03-19-zerion-api-supports-x402.md
│   │   └── ...
│   ├── pages/            # Static pages (about, knowledge base, etc.)
│   └── authors.json      # Author metadata
└── public/               # Generated output (gitignored)
```

## Build

```bash
python3 build.py
```

Preview locally:

```bash
python3 build.py --serve
# Open http://localhost:3000
```

## Writing a new post

Create a markdown file in `content/posts/`:

```markdown
---
title: "Your Post Title"
slug: your-post-title
date: 2026-04-01
published_at: 2026-04-01T12:00:00.000Z
feature_image: https://example.com/image.png
authors:
  - name: Your Name
    slug: your-name
    avatar: https://example.com/avatar.png
tags:
  - Zerion API
excerpt: "A short description for cards and SEO."
---

<p>Your HTML content here.</p>
```

Then rebuild: `python3 build.py`

## URL structure

All URLs match the original Ghost blog at `zerion.io/blog/` for zero-downtime migration:

| Pattern | Example |
|---------|---------|
| `/{slug}/` | `/best-solana-apis-for-developers/` |
| `/author/{slug}/` | `/author/vladimir/` |
| `/tag/{slug}/` | `/tag/zerion-api/` |
| `/changelog/` | Wallet update timeline |

## Deployment

The `public/` directory is a fully static site. Deploy to any static host:

```bash
# Vercel
vercel public/

# Cloudflare Pages
wrangler pages deploy public/

# Netlify
netlify deploy --dir=public --prod
```

## Images

Images are currently served from the Ghost CDN (`zerion.io/blog/content/images/`). To self-host, download them into an `assets/` directory and update the URLs in the markdown files.

## What's generated

- 302 blog posts
- 8 author listing pages
- 135 tag listing pages
- 12 static pages
- 1 changelog (37 wallet updates)
- 458 total HTML files
