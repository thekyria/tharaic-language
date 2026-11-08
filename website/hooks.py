"""MkDocs hooks that turn the repository into the website (see mkdocs.yml).

- README.md becomes the home page, and links between it and docs/ are fixed up.
- Links to files outside docs/ (data/, tools/, font/) point to GitHub instead.
- The lookup page, the site's CSS and JavaScript, and the web fonts are added.
- data/lexicon.yaml is exported to assets/lexicon.json for the lookup, and every
  inflected form to assets/forms.json for the word analysis.
"""
import os
import re
import sys

from mkdocs.structure.files import File

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from export_lexicon import forms_json, lexicon_json  # noqa: E402

REPO = "https://github.com/thekyria/tharaic-language/blob/main/"
OUTSIDE = r"(?:data|tools|font|tests|\.github)/"


def on_files(files, config):
    def add(uri, path):
        files.append(File.generated(config, uri, abs_src_path=path))

    add("index.md", os.path.join(ROOT, "README.md"))
    add("lookup.md", os.path.join(HERE, "lookup.md"))
    for name in sorted(os.listdir(os.path.join(HERE, "assets"))):
        add(f"assets/{name}", os.path.join(HERE, "assets", name))
    for name in sorted(os.listdir(os.path.join(ROOT, "font"))):
        if name.endswith(".woff2"):
            add(f"fonts/{name}", os.path.join(ROOT, "font", name))
    files.append(File.generated(config, "assets/lexicon.json", content=lexicon_json()))
    files.append(File.generated(config, "assets/forms.json", content=forms_json()))
    return files


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri == "index.md":
        markdown = re.sub(r"\]\(docs/", "](", markdown)
        markdown = re.sub(rf"\]\(({OUTSIDE})", rf"]({REPO}\1", markdown)
        # The home page gets a pointer to the lookup, which the README does not have
        markdown = markdown.replace(
            "\n## Contents\n",
            "\n> Try the [English → Tharaic lookup](lookup.md): type English, get the Tharaic words.\n\n## Contents\n",
            1)
    else:
        markdown = markdown.replace("](../README.md", "](index.md")
        markdown = re.sub(rf"\]\(\.\./({OUTSIDE})", rf"]({REPO}\1", markdown)
    return markdown
