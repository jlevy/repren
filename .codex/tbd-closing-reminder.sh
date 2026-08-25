#!/bin/bash
# Remind about close protocol after git push
# Installed by: tbd setup --auto

tbd_configured_fallback_version() {
  local config_path=$1
  local line configured_fallback_version
  local version_pattern='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$'

  while IFS= read -r line; do
    if [[ $line =~ ^tbd_fallback_version:[[:space:]]*([^[:space:]]+)[[:space:]]*$ ]]; then
      configured_fallback_version=${BASH_REMATCH[1]}
      if [[ $configured_fallback_version =~ $version_pattern ]]; then
        printf '%s\n' "$configured_fallback_version"
        return 0
      fi
      return 1
    fi
  done < "$config_path"
  return 1
}

tbd_local_can_read_repository() {
  command -v tbd &> /dev/null && tbd config get tbd_format >/dev/null 2>&1
}

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Check if this is a git push command and .tbd exists
if [[ "$command" == git\ push* ]] || [[ "$command" == *"&& git push"* ]] || [[ "$command" == *"; git push"* ]]; then
  # The hook may start in a subdirectory; check .tbd at the repo root.
  if ! repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
    exit 0
  fi
  cd "$repo_root" || exit 0
  if [ -d ".tbd" ]; then
    # Same format-compatible local selection and config-pinned fallback as
    # tbd-session.sh, so compatible patch releases do not rewrite this hook.
    export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:$PATH"
    if tbd_local_can_read_repository; then
      tbd closing
    elif configured_fallback_version=$(tbd_configured_fallback_version ".tbd/config.yml"); then
      if command -v npx &> /dev/null; then
        npx --yes "get-tbd@$configured_fallback_version" closing
      fi
    fi
  fi
fi

exit 0
