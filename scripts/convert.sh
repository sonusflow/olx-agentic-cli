#!/usr/bin/env bash
# convert.sh — Optional helper to strip YAML frontmatter for platforms
# that don't support it, or to extract specific sections.
#
# Usage:
#   ./scripts/convert.sh SKILL.md > SKILL_plain.md

set -euo pipefail

INPUT="${1:-SKILL.md}"

# Strip YAML frontmatter (everything between the first pair of ---)
awk 'BEGIN{skip=0} /^---$/{skip++; next} skip<2{next} {print}' "$INPUT"
