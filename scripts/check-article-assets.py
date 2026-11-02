"""Check local asset references in rendered HTML (run after a Jekyll build)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for attribute in ('src', 'href', 'poster'):
            if attribute in attrs:
                self.urls.append(attrs[attribute])
        if tag == 'meta' and attrs.get('property', attrs.get('name')) in (
            'og:image', 'twitter:image', 'image'
        ):
            self.urls.append(attrs.get('content', ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=Path('_site'))
    args = parser.parse_args()
    if not (args.site / 'index.html').is_file():
        parser.error('Build the site first; index.html is missing.')
    missing = set()
    checked = set()
    for page in args.site.rglob('*.html'):
        html = Assets()
        html.feed(page.read_text(encoding='utf-8'))
        for url in html.urls:
            parsed = urlsplit(url)
            if parsed.netloc and parsed.netloc != 'singularvector.github.io':
                continue
            path = unquote(parsed.path)
            if not path.startswith('/assets/'):
                continue
            checked.add(path)
            if not (args.site / path.lstrip('/')).is_file():
                missing.add((str(page.relative_to(args.site)), path))
    if missing:
        for page, path in sorted(missing):
            print(f'{page}: missing {path}')
        raise SystemExit(1)
    print(f'Assets: {len(checked)} local references resolve across rendered HTML.')


if __name__ == '__main__':
    main()
