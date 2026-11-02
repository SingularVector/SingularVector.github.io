# Blog images

Put article-specific screenshots and diagrams in a folder named for the article.
Use `shared/` for images used across posts, `site/` for the author image and icons,
and `archive/` for retained legacy images with no current source references.
Do not add article images directly to this directory.

Use `/assets/images/<article>/<filename>` in post front matter. In Markdown or HTML,
prefer Jekyll `relative_url` where appropriate, and provide useful alternative text.
Moving an image requires updating both the image source and any full-size link.
Article permalinks must remain unchanged.

The November 2026 reorganization changes image URLs; it does not create redirects
for external sites that hotlink the previous locations. Original image bytes are retained.
