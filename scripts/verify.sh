#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: verify.sh [--strict] [--only=<language>]...

Run the repository verify entry point, or detected language profile checks.

  --strict        Treat a missing tool as a failure.
  --only=<lang>   Run the named profile even without a stack marker.
                  Repeat to select more than one profile.

Resolution order: SBD_VERIFY_CMD, make verify, npm run verify, just verify,
then stack detection and the profile verify blocks.

Exit codes: 0 all pass or skip, 1 any failure, 2 usage.
EOF
}

strict=0
only=()
while (($# > 0)); do
  case "$1" in
    --strict)
      strict=1
      ;;
    --only=*)
      only+=("${1#--only=}")
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'verify: unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
profiles_dir="$script_dir/../languages"
profiles=(typescript python go java javascript csharp rust sql)

if [[ ! -d "$profiles_dir" ]]; then
  printf 'verify: profiles directory not found: %s\n' "$profiles_dir" >&2
  exit 2
fi

has_source() {
  local ext=$1 found
  found=$(find . \
    \( -name .git -o -name node_modules -o -name vendor -o -name build \
       -o -name target -o -name bin -o -name obj -o -name dist \) -prune -o \
    -name "*.$ext" -print 2>/dev/null | head -n 1)
  [[ -n "$found" ]]
}

has_root_file() {
  local pattern=$1 file
  for file in $pattern; do
    if [[ -e "$file" ]]; then
      return 0
    fi
  done
  return 1
}

has_marker() {
  case "$1" in
    typescript)
      [[ -f package.json && -f tsconfig.json ]] || return 1
      has_source ts || has_source tsx
      ;;
    javascript)
      [[ -f package.json ]] || return 1
      ! has_source ts && ! has_source tsx
      ;;
    python) [[ -f pyproject.toml ]] ;;
    go) [[ -f go.mod ]] ;;
    java) [[ -f pom.xml || -f build.gradle || -f build.gradle.kts ]] ;;
    csharp) has_source sln || has_source csproj ;;
    rust) [[ -f Cargo.toml ]] ;;
    sql) [[ -d migrations || -d db/migrations ]] || has_root_file '*.sql' ;;
    *) return 1 ;;
  esac
}

contains() {
  local needle=$1 item
  shift
  for item in "$@"; do
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

selected=()
if ((${#only[@]} > 0)); then
  for lang in "${only[@]}"; do
    if [[ ! -f "$profiles_dir/$lang.md" ]]; then
      printf 'verify: unknown profile: %s\n' "$lang" >&2
      exit 2
    fi
    if ! contains "$lang" "${selected[@]:-}"; then
      selected+=("$lang")
    fi
  done
else
  for lang in "${profiles[@]}"; do
    if has_marker "$lang"; then
      selected+=("$lang")
    fi
  done
fi

entry_label=""
entry_cmd=""
if [[ -n "${SBD_VERIFY_CMD:-}" ]]; then
  entry_label="env: SBD_VERIFY_CMD"
  entry_cmd="$SBD_VERIFY_CMD"
else
  makefile=""
  for candidate in Makefile makefile GNUmakefile; do
    if [[ -f "$candidate" ]]; then
      makefile="$candidate"
      break
    fi
  done
  if [[ -n "$makefile" ]] && grep -Eq '^verify[[:space:]]*:' "$makefile"; then
    entry_label="entry: make verify"
    entry_cmd="make verify"
  fi

  if [[ -z "$entry_cmd" && -f package.json ]]; then
    if command -v node >/dev/null 2>&1; then
      if node -e 'const p=require("./package.json"); process.exit(p.scripts && p.scripts.verify ? 0 : 1)' 2>/dev/null; then
        entry_label="entry: npm run verify"
        entry_cmd="npm run verify"
      fi
    elif grep -Eq '"verify"[[:space:]]*:' package.json; then
      entry_label="entry: npm run verify"
      entry_cmd="npm run verify"
    fi
  fi

  if [[ -z "$entry_cmd" ]]; then
    for candidate in justfile Justfile; do
      if [[ -f "$candidate" ]] && grep -Eq '^verify([[:space:]]+[^:]*)?:' "$candidate"; then
        entry_label="entry: just verify"
        entry_cmd="just verify"
        break
      fi
    done
  fi
fi

now_ms() {
  local ns
  if ns=$(date +%s%N 2>/dev/null) && [[ "$ns" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$((ns / 1000000))"
  else
    printf '%s000\n' "$(date +%s)"
  fi
}

extract_verify() {
  awk '
    /^```verify[[:space:]]*$/ { in_block = 1; next }
    in_block && /^```/ { exit }
    in_block && /^[[:space:]]*#/ { next }
    in_block && /^[[:space:]]*$/ { next }
    in_block { print }
  ' "$1"
}

first_word() {
  local value=$1
  value="${value#"${value%%[![:space:]]*}"}"
  printf '%s\n' "${value%%[[:space:]]*}"
}

tool_missing() {
  local cmd=$1 first rest tool
  first=$(first_word "$cmd")
  if [[ -z "$first" ]]; then
    return 0
  fi

  if [[ "$first" == "npx" ]]; then
    rest=${cmd#*npx}
    rest="${rest#"${rest%%[![:space:]]*}"}"
    if [[ "$rest" == --no-install* ]]; then
      rest=${rest#--no-install}
      rest="${rest#"${rest%%[![:space:]]*}"}"
      tool=$(first_word "$rest")
      if [[ -n "$tool" ]] && command -v "$tool" >/dev/null 2>&1; then
        return 1
      fi
      if [[ -n "$tool" && -x "./node_modules/.bin/$tool" ]]; then
        return 1
      fi
      return 0
    fi
  fi

  if [[ "$first" == "cargo" ]]; then
    rest=${cmd#*cargo}
    rest="${rest#"${rest%%[![:space:]]*}"}"
    tool=$(first_word "$rest")
    if [[ "$tool" == "deny" ]]; then
      if command -v cargo-deny >/dev/null 2>&1; then
        return 1
      fi
      return 0
    fi
  fi

  if [[ "$first" == ./* || "$first" == /* ]]; then
    if [[ -x "$first" ]]; then
      return 1
    fi
    return 0
  fi

  if command -v -- "$first" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

missing_tool_name() {
  local cmd=$1 first rest tool
  first=$(first_word "$cmd")
  if [[ "$first" == "npx" ]]; then
    rest=${cmd#*npx}
    rest="${rest#"${rest%%[![:space:]]*}"}"
    if [[ "$rest" == --no-install* ]]; then
      rest=${rest#--no-install}
      rest="${rest#"${rest%%[![:space:]]*}"}"
      tool=$(first_word "$rest")
      printf '%s\n' "$tool"
      return
    fi
  fi
  if [[ "$first" == "cargo" ]]; then
    rest=${cmd#*cargo}
    rest="${rest#"${rest%%[![:space:]]*}"}"
    tool=$(first_word "$rest")
    if [[ "$tool" == "deny" ]]; then
      printf 'cargo-deny\n'
      return
    fi
  fi
  printf '%s\n' "$first"
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

failures=0
checks=0
out_file="$tmp_dir/output"

run_check() {
  local label=$1 cmd=$2 status start end ms
  checks=$((checks + 1))
  : >"$out_file"

  if tool_missing "$cmd"; then
    if ((strict)); then
      status=fail
    else
      status=skip
    fi
    ms=0
  else
    start=$(now_ms)
    if eval "$cmd" >"$out_file" 2>&1; then
      status=pass
    else
      status=fail
    fi
    end=$(now_ms)
    ms=$((end - start))
  fi

  printf '%-58s | %-4s | %sms\n' "$label" "$status" "$ms"

  if [[ "$status" == "fail" ]]; then
    failures=$((failures + 1))
    if [[ -s "$out_file" ]]; then
      sed 's/^/  /' "$out_file"
    elif tool_missing "$cmd"; then
      printf '  missing tool: %s\n' "$(missing_tool_name "$cmd")"
    fi
  fi
}

printf '%-58s | %-4s | %s\n' "check" "status" "ms"
printf '%s\n' "--------------------------------------------------------------------"

if [[ -n "$entry_cmd" ]]; then
  run_check "$entry_label" "$entry_cmd"
elif ((${#selected[@]} > 0)); then
  for lang in "${selected[@]}"; do
    profile="$profiles_dir/$lang.md"
    commands=()
    while IFS= read -r line; do
      commands+=("$line")
    done < <(extract_verify "$profile")

    if ((${#commands[@]} == 0)); then
      checks=$((checks + 1))
      failures=$((failures + 1))
      printf '%-58s | %-4s | %sms\n' "$lang: missing verify block" "fail" "0"
      continue
    fi

    for cmd in "${commands[@]}"; do
      run_check "$lang: $cmd" "$cmd"
    done
  done
else
  checks=$((checks + 1))
  printf '%-58s | %-4s | %sms\n' "(no known stack or entry point)" "skip" "0"
fi

if ((failures > 0)); then
  printf '\n%d of %d checks failed\n' "$failures" "$checks"
  exit 1
fi

printf '\n%d checks passed or skipped\n' "$checks"
exit 0
