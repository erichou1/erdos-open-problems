#!/bin/zsh
set -eu
cd "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  print "EGMRA virtual environment is missing. Follow AGENT_SETUP.md Phase 1 first."
  read "?Press Enter to close..."
  exit 1
fi
exec .venv/bin/python -u operator_console.py
