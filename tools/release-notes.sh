#!/bin/sh
# Prints the GitHub release notes of one integration version: its "## X.Y.Z"
# section of CHANGELOG.md, without the heading: sh tools/release-notes.sh v1.0.0
# The app has no GitHub releases; its notes are in shellylanman/CHANGELOG.md.
set -eu
cd "$(dirname "$0")/.."
v="${1#v}"
[ -n "$v" ] || { echo "usage: $0 X.Y.Z" >&2; exit 2; }
notes="$(awk -v v="$v" '/^## / { if (on) exit; on = ($0 == "## " v); next } on { print }' CHANGELOG.md | sed -e '/./,$!d')"
[ -n "$notes" ] || { echo "no changelog section for $v" >&2; exit 1; }
printf '%s
' "$notes"
