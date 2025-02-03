A lightweight, minimal, statically compiled blog.
- [`staticjinja`](https://staticjinja.readthedocs.io/) for static compilation/watching
- [Jinja](https://jinja.palletsprojects.com/en/stable/) for templating
- [Python-Markdown](https://python-markdown.github.io/) for markdown -> HTML

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
