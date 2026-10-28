#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
root=$(cd -- "$script_dir/.." && pwd)
languages="$root/languages"
errors=0

fail() {
  printf 'check-profiles: %s\n' "$*" >&2
  errors=$((errors + 1))
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

if [[ ! -d "$languages" ]]; then
  printf 'check-profiles: languages directory not found: %s\n' "$languages" >&2
  exit 1
fi

: >"$tmp_dir/files"
for file in "$languages"/*.md; do
  if [[ ! -e "$file" ]]; then
    fail "no profile files found"
    break
  fi
  name=${file##*/}
  printf '%s\n' "${name%.md}" >>"$tmp_dir/files"
done
sort -o "$tmp_dir/files" "$tmp_dir/files"

profile_line=$(grep '^profiles=(' "$root/scripts/verify.sh" | head -n 1 || true)
if [[ -z "$profile_line" ]]; then
  fail "profiles array not found in scripts/verify.sh"
else
  registered=${profile_line#profiles=(}
  registered=${registered%)}
  printf '%s\n' $registered | sort >"$tmp_dir/registered"
  if ! diff -u "$tmp_dir/registered" "$tmp_dir/files"; then
    fail "profiles array does not match languages/*.md"
  fi
fi

for file in "$languages"/*.md; do
  name=${file##*/}
  name=${name%.md}
  # Check executable structure, not prose length or heading vocabulary.
  if ! awk '
    /^```verify[[:space:]]*$/ { in_block = 1; next }
    in_block && /^```/ { closed = 1; exit }
    in_block && /^[[:space:]]*#/ { next }
    in_block && NF { found = 1 }
    END { exit (found && closed) ? 0 : 1 }
  ' "$file"; then
    fail "$name: missing or empty verify block"
  fi
  refs=$(grep -o '`templates/boundaries/[^`]*`' "$file" | tr -d '`' || true)
  for ref in $refs; do
    if [[ ! -e "$root/$ref" ]]; then
      fail "$name: missing template $ref"
    fi
  done
  if LC_ALL=C grep -q '[^ -~]' "$file"; then
    fail "$name: contains non-ASCII characters"
  fi
done

if ((errors > 0)); then
  printf 'check-profiles: %d problem(s)\n' "$errors" >&2
  exit 1
fi

printf 'check-profiles: %d profiles consistent\n' "$(wc -l <"$tmp_dir/files" | tr -d ' ')"
