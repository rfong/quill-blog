---
tags: features, tag with spaces and cAsES, punct.**uat&&io?!!n
title: Tags and dates
description: Post with lots of tags. Also date in filename.
---

## Date
To annotate a markdown post with a date, prefix the filename with `YYYY-MM-DD`, for example `2025-02-04-post2.md`.

I've added a custom [Jinja filter](https://jinja.palletsprojects.com/en/stable/templates/#filters) `strftime` to render `datetime` objects in templates. 

By default, it will render to `%Y %B %d`.
```
{{ date | strftime }}
```

You can also pass in custom formats using standard [Python `strftime` notation](https://strftime.org/).
```
{{ date | strftime("%Y-%m-%d %H:%M:%S") }}
```

## Tags
Tags are automatically lowercased. Punctuation and whitespace will automatically be parsed out of tags and replaced with hyphens. For example:

- `tag with spaces` becomes `tag-with-spaces`
- `cAsEs` becomes `cases`
- `punct.**uat&&io?!!n` becomes `punct-uat-io-n`
