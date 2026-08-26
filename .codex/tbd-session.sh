#!/bin/bash
# Ensure the tbd CLI is available and run `tbd prime`.
# Installed by: tbd setup --auto. Runs on SessionStart and PreCompact.
#
# Local-first when the installed CLI can read this repository's tbd_format. Otherwise,
# use the exact version recorded by setup in .tbd/config.yml. Keeping the pin in config
# avoids rewriting this script for every compatible patch while retaining deterministic
# zero-install behavior.

# Prefer common local bin locations.
export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:$PATH"

repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$repo_root" ] || [ ! -f "$repo_root/.tbd/config.yml" ]; then
    echo "[tbd] Cannot locate repository .tbd/config.yml." >&2
    exit 1
fi
cd "$repo_root" || exit 1

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

if tbd_local_can_read_repository; then
    # Mint this working directory's agent id once, before priming, so tbd start has an
    # identity to claim under. Idempotent: SessionStart fires again on resume, clear, and
    # compact, and re-running must not mint a second agent for the same session.
    # Failure here is never fatal - identity resolution falls back to a derived name, and
    # an agent that cannot name itself precisely should still get its briefing.
    tbd whoami --ensure-id --quiet >/dev/null 2>&1 || true
    tbd prime "$@"
    exit $?
fi

# Read and validate the exact fallback before invoking a package runner. This prevents a
# malformed or hand-edited config value from becoming an executable package spec.
if ! configured_fallback_version=$(tbd_configured_fallback_version ".tbd/config.yml"); then
    echo "[tbd] .tbd/config.yml does not contain a valid exact tbd_fallback_version." >&2
    echo "[tbd] Run a current 'tbd setup --auto' to repair the managed launcher." >&2
    exit 1
fi

if command -v npx &> /dev/null; then
    if command -v tbd &> /dev/null; then
        echo "[tbd] Local tbd cannot read this repository format; using configured fallback get-tbd@$configured_fallback_version." >&2
    else
        echo "[tbd] tbd CLI not found; using configured fallback get-tbd@$configured_fallback_version." >&2
    fi
    npx --yes "get-tbd@$configured_fallback_version" prime "$@"
    exit $?
fi

if command -v tbd &> /dev/null; then
    echo "[tbd] Local tbd cannot read this repository format, and npx is unavailable." >&2
else
    echo "[tbd] tbd CLI not found and npx is unavailable." >&2
fi
echo "[tbd] Install it with: npm install -g get-tbd@$configured_fallback_version" >&2
exit 1
