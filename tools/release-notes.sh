#!/bin/sh
# Prints the GitHub release notes of one version: the integration's section of
# CHANGELOG.md and the app's of shellylanman/CHANGELOG.md (their "## X.Y.Z"
# sections, without the heading): sh tools/release-notes.sh v0.7.0
set -eu
cd "$(dirname "$0")/.."
v="${1#v}"
[ -n "$v" ] || { echo "usage: $0 X.Y.Z" >&2; exit 2; }
section() {
	awk -v v="$v" '/^## / { if (on) exit; on = ($0 == "## " v); next } on { print }' "$1" | sed -e '/./,$!d'
}
integration="$(section CHANGELOG.md)"
app="$(section shellylanman/CHANGELOG.md)"
[ -n "$integration$app" ] || { echo "no changelog section for $v" >&2; exit 1; }
if [ -n "$integration" ]; then printf '## Integration\n\n%s\n\n' "$integration"; fi
if [ -n "$app" ]; then printf '## App\n\n%s\n' "$app"; fi
