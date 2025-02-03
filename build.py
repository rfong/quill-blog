#!/usr/bin/env python3
### Build `staticjinja` site with markdown to html conversion.

import datetime
import os
from pathlib import Path
import re
import shutil

import markdown
from staticjinja import Site
import yaml  # PyYAML


# Matches a file prepended with %Y-%m-%d date, e.g. 2025-02-03-file.md
FILE_DATE_REGEX = re.compile("(\d{4}-\d{2}-\d{2}).*\..*")

# Regex of what to strip from tags.
# We can't use a simple latin alphabet [a-z0-9] exclusion because it doesn't 
# support other languages.
TAG_STRIP_REGEX = re.compile("[\s\"\'\(\)\+\,\-\/\:\;\<\=\>\[\]\_\`\{\|\}\~\/\!\@\#\$\%\^\&\*\.\?]+")

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

def get_pages_with_tag(tag):
  '''Return the list of pages associated with a tag.'''
  with open(get_tag_path(tag), "r") as tagfile:
    return [
      x.strip()
      for x in tagfile.readlines()
      if x
    ]
    '''
    list(filter(
      lambda x: x,
      Path(template.filename).read_text().split("\n")
    ))
    '''

def tag_context(template):
  '''Return context_aware metadata to annotate onto tag pages.'''
  tag = get_basename_without_ext(template.name)

  return {
    "tag": tag,
    "tagged_pages": get_pages_with_tag(tag),
  }

def md_context(template):
  '''Return context-aware metadata to annotate onto markdown templates.'''
  content = Path(template.filename).read_text()
  # Extract YAML front matter, if any
  YAML_SEP = "---\n"
  content = content.split(YAML_SEP)
  context = {}
  if len(content) >= 3:
    try:
      context = parse_front_matter(template, content[1])
      print("front matter:", context)
      content = content[2:]
    except yaml.YAMLError as exc:
      print("Error while parsing YAML front matter in %s" % template.name)
      print(exc)

  md_content = YAML_SEP.join(content)

  context.update({
    "post_content_html": markdowner.convert(md_content),
    "date_published": get_file_date(template),
    "category": get_page_category(template),
  })
  return context

def touch_file(path):
  '''Create an empty file at path'''
  # Create any nonexistent directories in path
  basedir = os.path.dirname(path)
  if not os.path.exists(basedir):
    os.makedirs(basedir)
  # Open the file and update the system time
  with open(path, 'a'):
    os.utime(path, None)

def parse_front_matter(template, front_matter):
  '''
  Clean or parse any front matter that is expected in a specific format.
  Note that these keys will clobber any other keys in the context!
  '''
  data = yaml.safe_load(front_matter)
  if "tags" in data:
    # Strip punctuation and replace with hyphens
    data["tags"] = [
      re.sub(TAG_STRIP_REGEX, "-", tag.lower())  # also lowercase
      for tag in data["tags"].split(", ")]
    # Update tag files
    for tag in data["tags"]:
      associate_page_tag(template, tag)

  return data

def get_tag_path(tag):
  '''Get the source path associated with a tag name.'''
  return "src/tags/{0}.txt".format(tag)

def associate_page_tag(template, tag):
  '''Associate a page with a tag.'''
  tag_path = get_tag_path(tag)
  touch_file(tag_path)
  # Get list of currently associated pages
  pages = get_pages_with_tag(tag)
  # Add this page and deduplicate
  pages.append(get_build_path(template))
  pages = list(set(pages))
  # Rewrite the tag file with the updated set
  with open(tag_path, "w") as myfile:
    myfile.write("\n".join(pages))
  print(tag, get_pages_with_tag(tag))

def get_page_category(template):
  '''The page category is the name of the first subdirectory'''
  path = template.name.split("/")
  return path[0] if len(path)>1 else None

def get_build_path(template):
  '''
  Output path transform, i.e. posts/post1.md -> posts/post1.html
  Note that this is relative to src/build dir.
  '''
  return os.path.splitext(template.name)[0] + ".html"

def render_md(site, template, **kwargs):
  '''Markdown to HTML render'''
  # newline to separate outputs from different builds
  print()

  # Get output filepath
  out = Path(os.path.join(site.outpath, get_build_path(template)))

  # Template = _{category}.html, or __toplevel.html if no category
  templateName = "_{0}.html".format(get_page_category(template) or "_toplevel")

  # Compile and stream the result
  os.makedirs(out.parent, exist_ok=True)
  site.get_template(templateName).stream(**kwargs).dump(str(out), encoding="utf-8")

def get_basename_without_ext(path):
  return os.path.splitext(os.path.basename(path))[0]

def render_tag(site, template, **kwargs):
  '''Tag page render'''
  # newline to separate outputs from different builds
  print()

  # Output path transform, i.e. tag/mytag.md -> build/tag/mytag/index.html
  out = Path(os.path.join(
    site.outpath, "tag", get_basename_without_ext(template.name), "index.html"))
  print("tag output path:", out)

  # Compile and stream the result
  os.makedirs(out.parent, exist_ok=True)
  site.get_template("_tags.html").stream(**kwargs).dump(str(out), encoding="utf-8")

def datetime_format_filter(value, format="%Y %B %d"):
  '''Datetime formatting filter function for Jinja templating.'''
  return value.strftime(format)

if __name__ == "__main__":
  # Pre-delete auto-compiled directories
  try:
    print("Cleaning build/...")
    shutil.rmtree("build")
    print("Cleaning src/tags/...")
    shutil.rmtree("src/tags")
    os.makedirs("src/tags", exist_ok=True)
  except FileNotFoundError:
    pass

  # Build site
  site = Site.make_site(
    # Template directory
    searchpath="src",
    # Output path
    outpath="build",
    # File specific contexts.
    # If there are multiple matches, the last regex wins.
    contexts=[
      (r".*\.md", md_context),
      (r"tags\/.*", tag_context),
    ],
    rules=[
      (r".*\.md", render_md),
      (r"tags\/.*", render_tag),
    ],
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
