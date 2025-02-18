#!/usr/bin/env python3
### Build `staticjinja` site with markdown to html conversion.

import datetime
import glob
import os
from pathlib import Path
import re
import shutil

import markdown
from staticjinja import Site
import yaml  # PyYAML


########################################
# Constants 

# YAML front matter separator
YAML_SEP = "---\n"

# Matches a file prepended with %Y-%m-%d date, e.g. 2025-02-03-file.md
FILE_DATE_REGEX = re.compile("(\d{4}-\d{2}-\d{2}).*\..*")

# Regex of what to strip from tags.
# We can't use a simple latin alphabet [a-z0-9] exclusion because it doesn't 
# support other languages.
TAG_STRIP_REGEX = re.compile("[\s\"\'\(\)\+\,\-\/\:\;\<\=\>\[\]\_\`\{\|\}\~\/\!\@\#\$\%\^\&\*\.\?]+")


########################################
# Staticjinja callbacks -- rendering and context annotation

markdowner = markdown.Markdown(
  output_format="html5",
  extensions=["extra", "admonition", "codehilite", "sane_lists", "smarty", "toc"],
)

def tag_context(template):
  '''Return context_aware metadata to annotate onto tag pages.'''
  tag = get_basename_without_ext(template.name)
  return {
    "tag": tag,
    "tagged_pages": get_pages_with_tag(tag),
  }

def md_context(template, norender=False):
  '''
  Return context-aware metadata to annotate onto markdown templates.
  If norender==True, only return summary context rather than all the context 
  needed to render.
  '''
  content = Path(template.filename).read_text()
  context = get_front_matter(template.filename)
  if norender is False:
    update_tags(template.filename, context)
  if context is not None:
    content = YAML_SEP.join(content.split(YAML_SEP)[2:])
  else:
    context = {}

  if template.name.startswith("index."):
    context.update(index_context(template))

  if norender is False:
    context["post_content_html"] = markdowner.convert(content)
    markdowner.reset()

  context.update({
    "date": get_file_date(template),
    "category": get_page_category(template),
  })
  return context

def index_context(template):
  '''Return additional context-aware metadata for index page.'''
  srcPaths = [
    path.removeprefix("src/")
    for path in glob.glob("src/posts/*.md")]
  posts = [
    dict(
      **{"url": get_build_path(path)},
      **md_context(site.get_template(path), norender=True),
    ) for path in srcPaths
  ]
  return {
    "posts": posts,
  }

def render_md(site, template, **kwargs):
  '''Markdown to HTML render'''
  # newline to separate outputs from different builds
  print()

  # Get output filepath
  out = Path(os.path.join(site.outpath, get_build_path(template.name)))

  # Template = _templates/{category}.html, or _templates/index.html if no category
  pgCat = get_page_category(template)
  templateName = ( \
    "_templates/{0}.html".format(get_page_category(template)) \
    if pgCat else \
    "_templates/index.html" \
  )

  # Compile and stream the result
  os.makedirs(out.parent, exist_ok=True)
  site.get_template(templateName).stream(**kwargs).dump(str(out), encoding="utf-8")

  # If it's a post, then index.md post index needs to be re-rendered too.
  if pgCat == "posts":
    rerender("index.md")

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
  site.get_template("_templates/tags.html").stream(**kwargs).dump(str(out), encoding="utf-8")


########################################
# Blog-structure-aware helpers

def rerender(srcPath):
  '''Manually re-render a template.'''
  print("re-render:", srcPath)
  site.render_templates([site.get_template(srcPath)])

def get_front_matter(filename):
  '''
  Parse YAML front matter from a file.
  Return {} if it was unreadable.
  Return None if front matter was not defined at all.
  '''
  print("get front matter for:", filename)
  content = Path(filename).read_text()
  # Extract YAML front matter, if any
  YAML_SEP = "---\n"
  content = content.split(YAML_SEP)
  if len(content) >= 3:
    try:
      return parse_front_matter(filename, content[1])
      print("front matter:", context)
    except yaml.YAMLError as exc:
      print("Error while parsing YAML front matter in %s" % filename)
      print(exc)
      return {}
  return None

def parse_front_matter(srcPath, front_matter):
  '''
  Handle front matter and update tag files.
  Note that these keys will clobber any other keys in the context!
  '''
  data = yaml.safe_load(front_matter)
  if "tags" in data:
    # Strip punctuation and replace with hyphens
    data["tags"] = [
      re.sub(TAG_STRIP_REGEX, "-", tag.lower())  # also lowercase
      for tag in data["tags"].split(", ")]
  return data

def update_tags(srcPath, front_matter):
  '''Update intermediate tag files for any tags associated with this path.'''
  print("update tags for", srcPath, front_matter)
  if front_matter and "tags" in front_matter:
    for tag in front_matter["tags"]:
      associate_page_tag(srcPath, tag)

def get_paths_with_tag(tag):
  '''
  Just get list of source paths associated with a tag.
  '''
  with open(get_tag_path(tag), "r") as tagfile:
    return [
      x.strip()
      for x in tagfile.readlines()
      if x
    ]

def get_pages_with_tag(tag):
  '''
  Return metadata on pages associated with a tag. 
  '''
  sourcePaths = get_paths_with_tag(tag)
  print("TAG SOURCE PATHS:", sourcePaths)
  return [
    dict( 
      **{"url": get_relative_path(get_build_path(path))},
      **md_context(site.get_template(path), norender=True),
    ) for path in sourcePaths
  ]

def get_relative_path(path):
  '''
  Get path relative to either the source or build directory.
  '''
  return path.removeprefix(os.getcwd()+"/src/")\
    .removeprefix(os.getcwd()+"/build/")

def associate_page_tag(srcPath, tag):
  '''
  Associate a page with a tag by writing its relative source path to an 
  intermediate file.
  '''
  tag_path = get_tag_path(tag)
  touch_file(tag_path)
  # Get list of currently associated pages
  pages = get_paths_with_tag(tag)
  # Add this page and deduplicate
  pages.append(get_relative_path(srcPath))
  pages = list(set(pages))
  # Rewrite the tag file with the updated set
  with open(tag_path, "w") as myfile:
    myfile.write("\n".join(pages))
  print(tag, get_paths_with_tag(tag))

def get_tag_path(tag):
  '''Get the source path associated with a tag name.'''
  return "src/tags/{0}.txt".format(tag)

def get_page_category(template):
  '''The page category is the name of the first subdirectory'''
  path = template.name.split("/")
  return path[0] if len(path)>1 else None

def get_build_path(templateName):
  '''
  Output path transform, i.e. posts/post1.md -> posts/post1.html
  Note that this is relative to src/build dir, does not include src/build.
  '''
  return os.path.splitext(templateName)[0] + ".html"

########################################
# Simple helpers

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

def touch_file(path):
  '''Create an empty file at path'''
  # Create any nonexistent directories in path
  basedir = os.path.dirname(path)
  if not os.path.exists(basedir):
    os.makedirs(basedir)
  # Open the file and update the system time
  with open(path, 'a'):
    os.utime(path, None)

def get_basename_without_ext(path):
  return os.path.splitext(os.path.basename(path))[0]

def strftime_filter(value, format="%Y %B %d"):
  '''Datetime formatting filter function for Jinja templating.'''
  return value.strftime(format)


########################################
# Main method when run as script

if __name__ == "__main__":
  # Pre-delete auto-compiled directories
  try:
    print("Cleaning build/ ...")
    shutil.rmtree("build")
    print("Cleaning src/tags/ ...")
    shutil.rmtree("src/tags")
    os.makedirs("src/tags", exist_ok=True)
    print("Copying public/ ...")
    shutil.copytree("public", "build/public")
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
      "strftime": strftime_filter,
    },
    # Global variables to make available in templates
    env_globals={
    },
  )
  # enable automatic reloading
  site.render(use_reloader=True)
