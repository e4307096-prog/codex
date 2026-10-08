#!/usr/bin/env bash
# Her ajan için ayrı git worktree oluşturur: ../<repo>-worktrees/<ajan>
set -e
root=$(git rev-parse --show-toplevel)
base="$(dirname "$root")/$(basename "$root")-worktrees"
mkdir -p "$base"
for a in ${@:-gameplay level assets}; do
  [ -d "$base/$a" ] && { echo "$a: zaten var"; continue; }
  git -C "$root" worktree add -B "agent/$a" "$base/$a" HEAD
  echo "$a -> $base/$a"
done
