"""Extract EPUB paragraphs into a private paragraph index; never bypasses DRM."""

import argparse
import json
import posixpath
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import unquote


def local_tag(element):
    return element.tag.rsplit("}", 1)[-1]


def own_text(element):
    """Avoid duplicating nested block paragraphs in unusual but parseable XHTML."""
    value = element.text or ""
    for child in element:
        if local_tag(child) not in {"p", "div", "h1", "h2", "h3"}:
            value += "".join(child.itertext())
        value += child.tail or ""
    return " ".join(value.split())


def spine_items(archive):
    root = ET.fromstring(archive.read("META-INF/container.xml"))
    package_path = next(
        e.attrib["full-path"] for e in root.iter() if local_tag(e) == "rootfile"
    )
    package = ET.fromstring(archive.read(package_path))
    manifest = {
        e.attrib["id"]: e.attrib["href"]
        for e in package.iter()
        if local_tag(e) == "item"
    }
    return [
        posixpath.normpath(
            posixpath.join(
                posixpath.dirname(package_path),
                unquote(manifest[e.attrib["idref"]].split("#")[0]),
            )
        )
        for e in package.iter()
        if local_tag(e) == "itemref"
    ]


def extract(archive, path):
    root = ET.fromstring(archive.read(path))
    paragraphs = []
    for element in root.iter():
        if local_tag(element) == "p":
            text = own_text(element)
            if text and (not paragraphs or paragraphs[-1] != text):
                paragraphs.append(text)
    if not paragraphs:
        raise ValueError("No se encontraron párrafos en este elemento del EPUB.")
    headings = [own_text(e) for e in root.iter() if local_tag(e) in {"h1", "h2"}]
    return {
        "chapter_title": next((h for h in headings if h), "Capítulo"),
        "paragraphs": paragraphs,
    }


def extract_all(archive, paths):
    paragraphs, chapters = [], []
    skipped = []
    for path in paths:
        try:
            part = extract(archive, path)
        except ValueError:
            skipped.append(path)
            continue
        paragraphs.extend(part['paragraphs'])
        chapters.extend([part['chapter_title']] * len(part['paragraphs']))
    if not paragraphs:
        raise ValueError('No se encontraron párrafos en el EPUB.')
    return {'paragraphs': paragraphs, 'chapters': chapters, 'skipped_items': skipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub", type=Path)
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar elementos del índice interno, desde 1",
    )
    parser.add_argument("--spine-index", type=int)
    parser.add_argument("--all", action="store_true", help="Indexar todos los elementos del EPUB")
    parser.add_argument("--output", type=Path, default=Path("data/book.json"))
    args = parser.parse_args()
    with zipfile.ZipFile(args.epub) as archive:
        paths = spine_items(archive)
        if args.list:
            for index, path in enumerate(paths, 1):
                print(f"{index}: {path}")
            return
        if args.all:
            data = extract_all(archive, paths)
        else:
            if args.spine_index is None or not 1 <= args.spine_index <= len(paths):
                parser.error("Elige --all o --spine-index después de consultar --list.")
            data = extract(archive, paths[args.spine_index - 1])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite an existing index without an explicit new destination.
    with args.output.open("x", encoding="utf-8") as target:
        json.dump(data, target, ensure_ascii=False, indent=2)
    print("Índice creado. Configura book_path y chapter_title en config.json.")


if __name__ == "__main__":
    main()
