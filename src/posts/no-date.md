---
title: Post with no date
description: In which `os` proceeds to incorrectly interpolate the file created timestamp
---

If you don't date a post, it will fallback to [`os.path.getctime`](https://docs.python.org/3.10/library/os.path.html#os.path.getctime). Unfortunately, there is no cross-platform way to get the actual file creation time. If you're on Unix, it will instead give you the time of the last metadata change.
