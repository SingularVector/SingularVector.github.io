"""Check generated metadata and discovery routes after a Jekyll build."""
from html.parser import HTMLParser
from pathlib import Path
import json

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.meta, self.links, self.canonicals = {}, [], []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property"))] = attrs.get("content")
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))

routes = ["", "about", "articles", "topics", "code-and-tools"] + ["topics/" + x for x in
    ["powershell", "linux", "identity", "infrastructure", "python", "git"]]
descriptions = []
for route in routes:
    page = Page(Path("_site") / route / "index.html")
    url = "https://singularvector.github.io/" + (route + "/" if route else "")
    assert page.canonicals == [url], (route, page.canonicals)
    description = page.meta["description"]
    assert description and "Hitchikers" not in description, route
    assert page.meta["og:description"] == description, route
    assert page.meta["twitter:description"] == description, route
    assert page.meta.get("og:image"), (route, "Missing sharing image")
    assert page.meta.get("twitter:image") == page.meta["og:image"], route
    assert page.meta.get("twitter:card") == "summary_large_image", route
    descriptions.append(description)
assert len(set(descriptions)) == len(routes), "Duplicate landing-page descriptions"
home = Page(Path("_site/index.html"))
for route in routes[5:]:
    assert "/" + route + "/" in home.links, route
assert "/code-and-tools/" in home.links
archive = Page(Path("_site/articles/index.html"))
assert "/topics/" in archive.links and "/search/" in archive.links
print("SEO: distinct descriptions, social metadata, canonical URLs and discovery links passed")
