#!/bin/bash
# Remind about close protocol after git push
# Installed by: tbd setup claude

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Check if this is a git push command and .tbd exists
if [[ "$command" == git\ push* ]] || [[ "$command" == *"&& git push"* ]] || [[ "$command" == *"; git push"* ]]; then
  if [ -d ".tbd" ]; then
    tbd closing
  fi
fi

exit 0
