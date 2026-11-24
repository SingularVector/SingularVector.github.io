"""Check internal page links and sitemap targets after a Jekyll build."""
from argparse import ArgumentParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ORIGIN = "https://singularvector.github.io"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.canonicals = []
        self.noindex = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))

        if tag == "meta" and attrs.get("name", "").lower() in ("robots", "googlebot"):
            directives = attrs.get("content", "").lower().replace(",", " ").split()
            self.noindex = self.noindex or "noindex" in directives or "none" in directives


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"))
    args = parser.parse_args()

    if not (args.site / "index.html").is_file():
        parser.error("Build the site first; index.html is missing.")

    # Compare exact spellings rather than Path.exists(): a case-insensitive
    # workstation can otherwise hide a link that fails on GitHub Pages.
    files = {path.relative_to(args.site).as_posix() for path in args.site.rglob("*") if path.is_file()}
    pages = {
        name: Page((args.site / name).read_text(encoding="utf-8"))
        for name in files if name.endswith(".html")
    }

    def resolve(path):
        name = unquote(path).lstrip("/")

        if name in files:
            return name

        directory_index = name.rstrip("/") + "/index.html" if name else "index.html"
        return directory_index if directory_index in files else None

    errors = set()
    targets = set()

    for name, page in pages.items():
        if name.startswith("assets/reports/") and not page.noindex:
            errors.add(f"{name}: synthetic report must retain noindex metadata")

        for href in page.links:
            target = urlsplit(urljoin(ORIGIN + "/" + name, href))

            if target.scheme not in ("http", "https") or target.netloc != urlsplit(ORIGIN).netloc:
                continue

            # Assets are covered by check-article-assets.py; this checks routes.
            if target.path.startswith("/assets/"):
                continue

            targets.add(target.path)

            if resolve(target.path) is None:
                errors.add(f"{name}: missing internal page {target.path}")

    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ET.parse(args.site / "sitemap.xml").getroot()

    if sitemap.tag != "{" + namespace["s"] + "}urlset":
        errors.add("sitemap.xml: expected a URL set")

    urls = [node.text or "" for node in sitemap.findall("s:url/s:loc", namespace)]

    if not urls or len(urls) != len(set(urls)):
        errors.add("sitemap.xml: missing or duplicate URL entries")

    for url in urls:
        target = urlsplit(url)

        if target.scheme != "https" or target.netloc != urlsplit(ORIGIN).netloc or target.query or target.fragment:
            errors.add(f"sitemap.xml: unexpected URL {url}")
            continue

        name = resolve(target.path)

        if name is None:
            errors.add(f"sitemap.xml: missing target {url}")
            continue

        if name.startswith("assets/reports/") or name == "googlea49631859f2e1ea8.html":
            errors.add(f"sitemap.xml: utility resource should be excluded: {url}")
            continue

        if name in pages:
            page = pages[name]

            if page.noindex:
                errors.add(f"sitemap.xml: noindex page included: {url}")

            if page.canonicals != [url]:
                errors.add(f"sitemap.xml: target is not self-canonical: {url}")

    if errors:
        raise SystemExit("\n".join(sorted(errors)))

    print(f"Discovery: {len(targets)} internal page targets resolve; {len(urls)} sitemap entries passed.")


if __name__ == "__main__":
    main()
