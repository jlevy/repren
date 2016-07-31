#!/bin/bash

set -euo pipefail

confirm_release=${1:?Usage: $0 tag-name
Publish release. Be sure to git push first.
Type the tag name to ensure it matches.
}

base=$(dirname $0)/..

release=$($base/repren --version)

if [[ "$release" != "$confirm_release" ]]; then
  echo "error: Confirming release failed: Didn't match expected: $release"
  exit 1
fi

if [[ "$(git status -s -uno | wc -l | xargs)" != "0" ]]; then
  echo "error: Uncomitted changes!"
  exit 1
fi


set -x

ghizmo create-release -a name=$release -a tag_name=$release -a prerelease=true
python $base/setup.py sdist upload -r pypi
