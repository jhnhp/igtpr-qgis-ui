#!/usr/bin/env python3
"""Static check for the mockup: every local href/src/iframe/JS-string path must resolve.

Run from anywhere:  python3 tools/check_links.py
Exits with status 1 if any broken reference is found.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = re.compile(r'^(https?:|mailto:|#|data:|javascript:)')
JS_PATH = re.compile(r'''["']([^"'\s<>+]*\.(?:html|css|js)(?:\?[^"'\s]*)?)["']''')


class RefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ('href', 'src') and value:
                self.refs.add(value)


def local_target(page: Path, ref: str):
    # A leading "/" is the tail of a path assembled in JS (e.g. "../roles/" + role + "/beranda/...").
    if EXTERNAL.match(ref) or ref.startswith('/'):
        return None
    path = ref.split('?')[0].split('#')[0]
    return (page.parent / path).resolve() if path else None


def main() -> int:
    pages = sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts)
    broken = 0
    for page in pages:
        text = page.read_text(encoding='utf-8')
        collector = RefCollector()
        collector.feed(text)
        for ref in sorted(collector.refs | set(JS_PATH.findall(text))):
            target = local_target(page, ref)
            if target and not target.is_file():
                print(f'BROKEN  {page.relative_to(ROOT)} -> {ref}')
                broken += 1
    print(f'{len(pages)} pages checked, {broken} broken reference(s)')
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
