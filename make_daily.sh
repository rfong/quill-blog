#!/bin/zsh
# Makes a post dated with today's date.
# Usage: `make daily post-title`

if [ ! -z "$1" ]; then
  # use title as part of file name
  fname=src/posts/`date +"%Y-%m-%d"`-$1.md
else
  # no title
  fname=src/posts/`date +"%Y-%m-%d"`.md
fi

if [ -f "$fname" ]; then
  echo "$fname already exists."
else
  cp src/_templates/daily_post.md $fname
  echo 'date: '`date +"%Y-%m-%d %H:%M:%S"` >> $fname
  echo "---" >> $fname
  echo "created $fname"
fi

# Open file for editing
vim $fname
