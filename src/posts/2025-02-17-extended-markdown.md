---
tags: features
title: Footnotes, code blocks, other Markdown extended syntax
---

### Table of contents

[TOC]

(use `[TOC]` in markdown to generate a table of contents)

### Footnote

Here's a simple footnote.[^1]

Here's a longer footnote.[^bignote]

### Code block with syntax highlighting

```
:::python
from pygments.formatters import HtmlFormatter
from markdown.extensions.codehilite import CodeHiliteExtension

# 79 char line:
0123456789012345678901234567890123456789012345678901234567890123456789012345678
```

### Table

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

### References

- [Markdown extended syntax guide](https://www.markdownguide.org/extended-syntax/)
- [Python-Markdown extensions](https://python-markdown.github.io/extensions/) (allows you to write [custom extensions](https://python-markdown.github.io/extensions/api/))


[^1]: This is the first footnote.

[^bignote]: Here's one with multiple paragraphs and code.

    Indent paragraphs to include them in the footnote.

    `{ my code }`

    Add as many paragraphs as you like.
