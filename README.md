Quill is a lightweight, minimal, statically compiled blog framework written in 
Python on top of staticjinja. Implements tag collection, post categories, and 
some other small convenience features.
[Extended Markdown syntax](https://www.markdownguide.org/extended-syntax/) 
is supported.

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

## Make targets

- `make watch`: compile with autoreload
- `make serve`: serve rendered files on port 8080
- `make test`: run unit tests
- `make static`: copy over static files
- `make daily title=my-post-title`: generate a new dated post without having to type out the date

Note: Static file watching has been deprecated in `staticjinja` and I have not 
had time to implement my own static file watcher yet. So to copy over static 
files to the build dir, you can either manually restart `make watch` or 
manually run `make static`. Yes, it's janky.

## Structure

- `src/` - source files
- `build/` - rendered for web
- `public/` - static source files

Build settings can be found in `build.py`.

A bit of minimal site config is in `_config.yml`.

## Markdown compilation and HTML templates
Markdown files are automatically categorized by subdirectory, and compiled to 
HTML template partials matching their subdirectory name in `src/_templates`. 
This behavior is described in the `render_md` function in `build.py`.

For example, `src/posts/post1.md` will look for a template at 
`src/_templates/posts.html`.

Top level md files, e.g. `src/index.md`, will use `src/_templates/index.html` 
if no other template is specified.

## Front matter (title, tags, etc)
YAML front matter is parsed out of the tops of Markdown source files with 
`PyYAML`. Look in `src/posts` for examples.

## Post dates
Post dates are parsed out of markdown basename prefixes if present in 
`%Y-%m-%d` format, for example `2025-02-03-my-post.md`.

## Tags
`tags` are automatically parsed from YAML front matter and compiled to 
`build/tag/<tag_name>/index.html` as pages that display all posts tagged with 
that tag.

As an intermediate build step, `render_md(...)` generates tag files in 
`src/tags/`. Yes it's very janky. These are then rendered using the 
`tags.html` template.

Note that the approach is lazy about cleanup, and will not delete empty tag 
files on render autoreload, since this doesn't matter until it's time to push 
your changes anyway. For a clean build, quit and rerun `make watch`.


# Miscellaneous notes

## Compress font files for web

```
brew install woff2
for f in *.otf; do woff2_compress $f; done
```

## Syntax highlighting CSS

The [CodeHilite Python-Markdown extension](https://python-markdown.github.io/extensions/code_hilite/) is used for syntax highlighting.

Regenerate with:
```
pygmentize -S default -f html -a .codehilite >> public/codehilite.css
```

# Todo

- [ ] Clean up the CSS files with Sass
