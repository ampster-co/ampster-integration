#!/bin/zsh
# release.sh - Commit, tag, push, and create a GitHub release for Ampster integration
#
# -----------------------------
# Automated Release Script
# -----------------------------
#
# This script automates the process of committing changes, tagging a new version, pushing to GitHub,
# and creating a GitHub release for the Ampster Home Assistant integration.
#
# Usage:
#   ./release.sh "Your commit message here" [vX.Y.Z]
#
# Arguments:
#   1. Commit message (required)
#   2. Version tag (optional, e.g., v1.0.9). If omitted, the script will suggest the next patch version.
#      Press Enter to accept the suggestion or type a custom version.
#
# Requirements:
#   - git (with a clean working directory or staged changes)
#   - GitHub CLI (`gh`) installed and authenticated
#   - Push access to the repository
#
# What it does:
#   1. Stages all changes and commits with the provided message.
#   2. Pushes the commit to the main branch.
#   3. Determines the latest version tag and suggests the next patch version.
#   4. Prompts for a version tag (accepts Enter for the suggestion).
#   5. Tags the commit and pushes the tag.
#   6. Creates a GitHub release for the new tag with the commit message as release notes.
#
# Example:
#   ./release.sh "Fix bug in coordinator logic"
#   (Prompts: Enter version tag [v1.0.9]: )
#
#   ./release.sh "Add new feature" v1.1.0
#
# If you encounter errors, ensure you have push access and that the GitHub CLI is set up.

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

# Commit only if there are staged changes
git diff --cached --quiet || git commit -m "$COMMIT_MSG"

git push origin main

# Get latest tag and suggest next version if not provided
if [ -z "$TAG" ]; then
  LATEST_TAG=$(git tag --list 'v*' --sort=-v:refname | head -n1)
  if [[ $LATEST_TAG =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    MAJOR=$(echo $LATEST_TAG | sed -E 's/v([0-9]+)\..*/\1/')
    MINOR=$(echo $LATEST_TAG | sed -E 's/v[0-9]+\.([0-9]+)\..*/\1/')
    PATCH=$(echo $LATEST_TAG | sed -E 's/v[0-9]+\.[0-9]+\.([0-9]+)/\1/')
    NEXT_PATCH=$((PATCH+1))
    NEXT_TAG="v${MAJOR}.${MINOR}.${NEXT_PATCH}"
  else
    NEXT_TAG="v1.0.0"
  fi
  echo "Latest tag: $LATEST_TAG"
  printf "Enter version tag [%s]: " "$NEXT_TAG"
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
