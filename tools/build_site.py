"""Build a static local preview in a new directory; never upload anything.

No external renderer, account, API or paid service. A real HTTPS base URL must
be supplied explicitly before canonical/sitemap metadata can be generated.
"""
import argparse
import hashlib
import html
import json
import os
import posixpath
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import quote, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_METADATA = {
    "owner": "enayzuin",
    "license": "MIT",
    "distribution_version": "0.1.1",
    "repository_url": "https://github.com/enayzuin/zuuuin-skills",
    "site_url": "https://enayzuin.github.io/zuuuin-skills/",
}
STYLE = """body{font:17px/1.6 system-ui,sans-serif;color:#202d38;background:#f7f8fa;margin:0}main{max-width:1050px;margin:auto;padding:1.5rem}a{color:#07589b}nav{display:flex;gap:1rem;flex-wrap:wrap}header{border-bottom:1px solid #ccd3da;padding-bottom:1rem}pre{background:#e9eef2;padding:1rem;overflow:auto}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #ccd3da;padding:.6rem;text-align:left}blockquote{border-left:4px solid #607b8f;padding-left:1rem}h1,h2,h3{line-height:1.25}footer{margin-top:3rem;border-top:1px solid #ccd3da;font-size:.9rem}@media(max-width:600px){main{padding:1rem}body{font-size:16px}}"""

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def html_name(name):
    return {"README.md": "index.html", "README.en.md": "index.en.html"}.get(name, name[:-3] + ".html")

def inline(value, source, pages):
    """Escape text and render only explicit Markdown links, without active HTML."""
    parts, cursor = [], 0
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", value):
        parts.append(html.escape(value[cursor:match.start()]))
        label, target = match.groups()
        url = urlsplit(target)
        if url.scheme and url.scheme not in {"http", "https", "mailto"}:
            raise ValueError("Unsupported link scheme")
        if not url.scheme and url.path:
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), url.path))
            if resolved in pages:
                relative = posixpath.relpath(html_name(resolved), posixpath.dirname(html_name(source)) or ".")
                target = urlunsplit(("", "", relative, url.query, url.fragment))
        parts.append('<a href="' + html.escape(target, quote=True) + '">' + html.escape(label) + '</a>')
        cursor = match.end()
    parts.append(html.escape(value[cursor:]))
    return "".join(parts)

def render_markdown(value, source, pages):
    lines = value.splitlines(); out = []; index = 0; headings = {}; title = "Zuuuin Skills"
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            block = []; index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index]); index += 1
            out.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
        elif line.startswith("|") and index + 1 < len(lines) and re.fullmatch(r"[| :\-]+", lines[index + 1]):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                if not re.fullmatch(r"[| :\-]+", lines[index]):
                    rows.append([cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", lines[index].strip().strip("|"))])
                index += 1
            out.append("<table><thead><tr>" + "".join("<th>" + inline(c, source, pages) + "</th>" for c in rows[0]) + "</tr></thead><tbody>")
            for row in rows[1:]:
                out.append("<tr>" + "".join("<td>" + inline(c, source, pages) + "</td>" for c in row) + "</tr>")
            out.append("</tbody></table>"); continue
        elif re.match(r"^#{1,6} ", line):
            level = len(line.split(" ", 1)[0]); text = line[level + 1:]
            if level == 1 and title == "Zuuuin Skills": title = text
            slug = re.sub(r"[^\w\- ]", "", text.lower()).strip().replace(" ", "-")
            number = headings.get(slug, 0); headings[slug] = number + 1
            anchor = slug + ("-" + str(number) if number else "")
            out.append(f'<h{level} id="{html.escape(anchor, quote=True)}">' + inline(text, source, pages) + f"</h{level}>")
        elif line.startswith("- "):
            out.append("<ul>")
            while index < len(lines) and lines[index].startswith("- "):
                out.append("<li>" + inline(lines[index][2:], source, pages) + "</li>"); index += 1
            out.append("</ul>"); continue
        elif line.startswith("> "): out.append("<blockquote>" + inline(line[2:], source, pages) + "</blockquote>")
        elif line: out.append("<p>" + inline(line, source, pages) + "</p>")
        index += 1
    return title, "\n".join(out)

def build(destination, base_url=None):
    if base_url is not None:
        u = urlsplit(base_url)
        if (u.scheme != "https" or not u.hostname or u.username or u.password
                or "?" in base_url or "#" in base_url or "\\" in base_url
                or any(ord(char) <= 32 or ord(char) == 127 for char in base_url)):
            raise ValueError("Explicit HTTPS base URL without credentials/query/fragment required")
        u.port  # Refuse malformed ports before creating the destination.
        base_url = base_url.rstrip("/") + "/"
    if destination.is_symlink() or destination.exists(): raise ValueError("Output must be new")
    destination = destination.resolve()
    if destination == ROOT or destination.is_relative_to(ROOT): raise ValueError("Output must be outside the package")
    if not destination.parent.is_dir(): raise ValueError("Output parent must exist")
    files = []
    for directory, dirs, names in os.walk(ROOT, followlinks=False):
        if Path(directory) == ROOT:
            dirs[:] = [name for name in dirs if name != ".git"]
            names = [name for name in names if name != ".git"]
        if any((Path(directory) / name).is_symlink() for name in dirs + names):
            raise ValueError("Symlinks are not site inputs")
        if ".git" in dirs or ".git" in names: raise ValueError("Embedded Git history refused")
        files.extend(Path(directory) / name for name in names)
    files.sort()
    catalog = json.loads((ROOT / "catalog/skills.json").read_text(encoding="utf-8"))
    if not all(catalog.get(key) == value for key, value in PUBLIC_METADATA.items()):
        raise ValueError("Selected public metadata changed; review site wording")
    version = catalog["runtime"]["version"]
    if version != "0.1.1": raise ValueError("Runtime candidate changed")
    distribution_version = catalog["distribution_version"]
    pages = {p.relative_to(ROOT).as_posix(): p for p in files if p.suffix == ".md" and ".well-known" not in p.parts}
    html_paths = {html_name(name) for name in pages}
    if any((ROOT / name).exists() for name in html_paths | {"site-style.css", "robots.txt", "sitemap.xml", ".nojekyll"}):
        raise ValueError("Generated site names conflict with package inputs")
    destination.mkdir(mode=0o700)
    for file in files:
        target = destination / file.relative_to(ROOT); target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(file, target)
    for source, path in sorted(pages.items()):
        name = html_name(source); prefix = posixpath.relpath(".", posixpath.dirname(name) or ".")
        relative = lambda item: posixpath.relpath(item, posixpath.dirname(name) or ".")
        title, body = render_markdown(path.read_text(encoding="utf-8"), source, pages)
        canonical = '<link rel="canonical" href="' + html.escape(base_url + quote(name), quote=True) + '">' if base_url else ""
        doc = '<!doctype html><html lang="' + ("en" if source == "README.en.md" else "pt-BR") + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>' + html.escape(title) + ' · Zuuuin Skills ' + html.escape(distribution_version) + '</title><link rel="stylesheet" href="' + relative("site-style.css") + '"><link rel="alternate" type="text/markdown" href="' + html.escape(relative(source), quote=True) + '"><link rel="describedby" href="' + relative("llms.txt") + '">' + canonical + '</head><body><main><header><p>Zuuuin Skills ' + html.escape(distribution_version) + ' · runtime ' + html.escape(version) + ' · prévia local</p><nav aria-label="Navegação"><a href="' + relative("index.html") + '">Início</a><a href="' + relative("docs/index.html") + '">Skills</a><a href="' + relative("docs/installation.html") + '">Instalação</a><a href="' + relative("docs/site.html") + '">Site e limites</a><a href="' + relative("LICENSE-STATUS.html") + '">Direitos</a></nav></header>' + body + '<footer>Conteúdo próprio de enayzuin sob MIT. Prévia local com indexação desabilitada. Nenhum envio ou hospedagem foi executado por este gerador.</footer></main></body></html>\n'
        target = destination / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(doc, encoding="utf-8")
    (destination / "site-style.css").write_text(STYLE + "\n", encoding="utf-8")
    (destination / ".nojekyll").write_bytes(b"")
    (destination / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    if base_url:
        ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
        tree = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
        for name in sorted(html_paths):
            ET.SubElement(ET.SubElement(tree, "url"), "loc").text = base_url + quote(name)
        ET.ElementTree(tree).write(destination / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    return {"status": "built_local_only", "runtime_version": version, "distribution_version": distribution_version, "owner": catalog["owner"], "license": catalog["license"], "html_pages": len(pages), "copied_public_resources": len(files), "canonical_and_sitemap": bool(base_url), "indexing": "disallowed", "uploads": 0, "files": {p.relative_to(destination).as_posix(): digest(p) for p in sorted(destination.rglob("*")) if p.is_file()}}

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", required=True, type=Path); parser.add_argument("--base-url")
    args = parser.parse_args()
    try: print(json.dumps(build(args.output, args.base_url), ensure_ascii=False, sort_keys=True)); return 0
    except (OSError, ValueError, KeyError) as error: print(str(error), file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
