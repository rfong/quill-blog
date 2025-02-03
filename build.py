#!/usr/bin/env python3
### Build `staticjinja` site with markdown to html conversion.

import datetime
import os
from pathlib import Path
import re
import shutil

import markdown
from staticjinja import Site


# Matches a file prepended with %Y-%m-%d date, e.g. 2025-02-03-file.md
FILE_DATE_REGEX = re.compile("(\d{4}-\d{2}-\d{2}).*\..*")

markdowner = markdown.Markdown(output_format="html5")

def get_file_date(template):
  '''Get timestamp associated with file'''
  # try to get timestamp from filename if it exists
  match = re.match(FILE_DATE_REGEX, template.filename.split("/")[-1])
  if match:
    # parse the first capture group
    return datetime.datetime.strptime(match[1], "%Y-%m-%d")
  else:
    # as fallback, get timestamp from last file modified date
    template_mtime = os.path.getmtime(template.filename)
    return datetime.datetime.fromtimestamp(template_mtime)

def md_context(template):
  '''Return context-aware metadata to annotate onto markdown templates.'''
  return {
    "post_content_html": markdowner.convert(
      Path(template.filename).read_text()
    ),
    "date_published": get_file_date(template),
    "category": get_page_category(template),
   }

def get_page_category(template):
  '''The page category is the name of the first subdirectory'''
  path = template.name.split("/")
  return path[0] if len(path)>1 else None

def render_md(site, template, **kwargs):
  '''Render markdown to HTML'''
  # Output path transform, i.e. posts/post1.md -> build/posts/post1.html
  out = site.outpath / Path(template.name).with_suffix(".html")

  # Template = _{category}.html, or __toplevel.html if no category
  templateName = "_{0}.html".format(get_page_category(template) or "_toplevel")

  # Compile and stream the result
  os.makedirs(out.parent, exist_ok=True)
  site.get_template(templateName).stream(**kwargs).dump(str(out), encoding="utf-8")

def datetime_format_filter(value, format="%Y %B %d"):
  '''Datetime formatting filter function for Jinja templating.'''
  return value.strftime(format)

if __name__ == "__main__":
  # Pre-delete build directory
  try:
    shutil.rmtree("build")
  except FileNotFoundError:
    pass

  # Build site
  site = Site.make_site(
    # Template directory
    searchpath="src",
    # Output path
    outpath="build",
    # File specific contexts
    contexts=[(r".*\.md", md_context)],
    rules=[(r".*\.md", render_md)],
    # Custom Jinja filters
    filters={
      "datetime_format": datetime_format_filter,
    },
    # Global variables to make available in templates
    env_globals={
    },
  )
  # enable automatic reloading
  site.render(use_reloader=True)
