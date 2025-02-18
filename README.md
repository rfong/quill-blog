A lightweight, minimal, statically compiled blog.
- [`staticjinja`](https://staticjinja.readthedocs.io/) for static compilation/watching
- [Jinja](https://jinja.palletsprojects.com/en/stable/) for templating
- [Python-Markdown](https://python-markdown.github.io/) for markdown -> HTML
- [PyYAML](https://pypi.org/project/PyYAML/) for YAML

# Setup

MacOS:
```
brew install fswatch woff2
python -m venv venv              # make python virtual env
source venv/bin/activate         # activate virtual env
pip install -r requirements.txt  # install requirements
```

# Usage
- `make watch`: compile with autoreload
- `make serve`: serve rendered files on port 8080; can change this from `Makefile`

Build settings can be found in the bottom of `build.py`.
- source files live in `src/`
- render files live in `build/`
- static files live in `public/`

I was too lazy to write a static file watcher, so manually restart `make watch` after updating static files.

## Markdown compilation
Markdown files are automatically categorized by subdirectory, and compiled to HTML template partials matching their subdirectory name. This behavior is described in the `render_md` function in `build.py`.
- For example, `src/posts/post1.md` will look for a template at `src/_posts.html`.
- Top level md files, e.g. `src/index.md`, will use `src/__toplevel.html` if no other template is specified.

## Front matter
YAML front matter is parsed out of the tops of Markdown source files usings `PyYAML`.
```
---
# Tags are a list of comma separated strings that will be cleaned.
tags: tag1, tag2, tag with spaces and cAsEs, tag!with!punctuation!!

# You can specify a different template.
template: my_template  # this will search for a partial `src/_my_template.html`
---

example post content
```

## Post dates
Post dates are parsed out of markdown basenames if present in `%Y-%m-%d` 
format, e.g. `2025-02-03-my-post.md`.

## Tags
`tags` are automatically parsed from YAML front matter and compiled to `build/tag/<tag_name>/index.html` as pages that display all posts tagged with that tag.

As an intermediate build step, `render_md(...)` generates tag files in `src/tags/`. These are compiled using the template at `src/_tags.html`.

Note that the approach is lazy about cleanup, and will not delete empty tag files on render autoreload. For a clean build, quit and rerun the watch command.

# Miscellaneous notes

## Compress font files

```
brew install woff2
for f in *.otf; do woff2_compress $f; done
```
