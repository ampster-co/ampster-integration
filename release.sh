#!/bin/zsh
# release.sh - Commit, tag, push, and create a GitHub release for Ampster integration
#
# Usage:
#   ./release.sh "Your commit message here" [vX.Y.Z]
#
# - The commit message is required.
# - The version tag (e.g., v1.0.9) is optional. If not provided, you will be prompted.
# - Requires git and GitHub CLI (gh) to be installed and authenticated.

set -e

if [ -z "$1" ]; then
  echo "Error: Commit message is required."
  echo "Usage: $0 \"Your commit message\" [vX.Y.Z]"
  exit 1
fi

COMMIT_MSG="$1"
TAG="$2"

# Stage all changes
git add .

git commit -m "$COMMIT_MSG"

git push origin main

# Get latest tag and suggest next version if not provided
if [ -z "$TAG" ]; then
  LATEST_TAG=$(git tag --list 'v*' --sort=-v:refname | head -n1)
  if [[ $LATEST_TAG =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    MAJOR=${BASH_REMATCH[1]}
    MINOR=${BASH_REMATCH[2]}
    PATCH=${BASH_REMATCH[3]}
    NEXT_PATCH=$((PATCH+1))
    NEXT_TAG="v${MAJOR}.${MINOR}.${NEXT_PATCH}"
  else
    NEXT_TAG="v1.0.0"
  fi
  echo "Latest tag: $LATEST_TAG"
  echo -n "Enter version tag [${NEXT_TAG}]: "
  read USER_TAG
  if [ -z "$USER_TAG" ]; then
    TAG="$NEXT_TAG"
  else
    TAG="$USER_TAG"
  fi
fi

git tag "$TAG"
git push origin "$TAG"

gh release create "$TAG" --title "$TAG" --notes "$COMMIT_MSG"

echo "Release $TAG created successfully."
