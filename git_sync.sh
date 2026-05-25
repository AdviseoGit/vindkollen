#!/usr/bin/env bash
# git_sync.sh — pull latest + stage/commit/push for a project repo
# Usage: git_sync.sh <project_path> [commit_message]
set -euo pipefail

PROJECT_PATH="${1:?Usage: git_sync.sh <project_path> [commit_message]}"
COMMIT_MSG="${2:-feat: automated content update $(date +%Y-%m-%d)}"

if [ -z "${GITHUB_PAT:-}" ]; then
  echo "ERROR: GITHUB_PAT env var not set — cannot push to GitHub" >&2
  exit 1
fi

cd "$PROJECT_PATH"

git config user.email "agent@adviseo.se"
git config user.name "AgentSim"

# Rewrite remote to HTTPS+PAT regardless of whether it was SSH or plain HTTPS
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$REMOTE_URL" == git@github.com:* ]]; then
  REPO_PATH="${REMOTE_URL#git@github.com:}"
  git remote set-url origin "https://oauth2:${GITHUB_PAT}@github.com/${REPO_PATH}"
elif [[ "$REMOTE_URL" == https://github.com/* ]]; then
  REPO_PATH="${REMOTE_URL#https://github.com/}"
  git remote set-url origin "https://oauth2:${GITHUB_PAT}@github.com/${REPO_PATH}"
fi

echo "=== Pulling latest ==="
git pull origin main --no-edit --no-rebase 2>&1 || true

echo "=== Checking for changes ==="
if git diff --quiet && git diff --cached --quiet; then
  echo "GIT_NO_CHANGES — nothing to commit"
  exit 0
fi

git add -A
git commit -m "$COMMIT_MSG"

echo "=== Pushing ==="
git push -f origin main 2>&1 && echo "GIT_PUSH_SUCCESS" || { echo "GIT_PUSH_FAILED"; exit 1; }
