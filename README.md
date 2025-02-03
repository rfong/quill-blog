A lightweight, minimal, statically compiled blog.
- [`staticjinja`](https://staticjinja.readthedocs.io/) for static compilation/watching
- [Jinja](https://jinja.palletsprojects.com/en/stable/) for templating
- [Python-Markdown](https://python-markdown.github.io/) for markdown -> HTML
- [PyYAML](https://pypi.org/project/PyYAML/) for YAML

# Setup
```
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
- static files live in `public/` # TODO

## Markdown compilation
Markdown files are automatically categorized by subdirectory, and compiled to HTML template partials matching their subdirectory name. This behavior is described in the `render_md` function in `build.py`.
- For example, `src/posts/post1.md` will look for a template at `src/_posts.html`.
- Top level md files, e.g. `src/*.md`, will use `src/__toplevel.html`.

YAML front matter is parsed out of the tops of Markdown source files usings `PyYAML`.

## Tags
`tags` are automatically parsed from YAML front matter and compiled to `build/tag/<tag_name>/index.html` as pages that display all posts tagged with that tag.

As an intermediate build step, `render_md(...)` generates tag files in `src/tags/`. These are compiled using the template at `src/_tags.html`.

Note that the approach is lazy about cleanup, and will not delete empty tag files on render autoreload. For a clean build, quit and rerun the watch command.
