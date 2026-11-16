#!/usr/bin/env bash
# skills-git-sync.sh - cron entry point for the weekly skills <-> GitHub reconcile.
#
# The real script lives in the git-tracked skill (single source of truth):
#   ~/.hermes/skills/github/github-auth/scripts/skills-git-sync.sh
#
# This file must stay a REAL file inside ~/.hermes/scripts/: the Hermes cron guard
# resolves the job script path and refuses anything landing outside
# HERMES_HOME/scripts/ ("Blocked: script path resolves outside the scripts
# directory"), so a symlink to the skill copy can never run as a cron script.
# Wrapping keeps the logic versioned in the skills repo instead of duplicating it.
#
# stdout is delivered verbatim; exit code is the real script's exit code.
set -uo pipefail

REAL="${SKILLS_SYNC_SCRIPT:-$HOME/.hermes/skills/github/github-auth/scripts/skills-git-sync.sh}"

if [ ! -f "$REAL" ]; then
  echo "skills-sync: FAILED - real script missing at $REAL (skill moved? fix ~/.hermes/scripts/skills-git-sync.sh)"
  exit 1
fi

exec bash "$REAL" "$@"
