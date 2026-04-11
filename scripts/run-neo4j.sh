#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_NEO4J_HOME="$ROOT/backend/neo4j-mostar-industries"

export NEO4J_HOME="$APP_NEO4J_HOME"
export NEO4J_CONF="$APP_NEO4J_HOME/conf"

mkdir -p \
  "$APP_NEO4J_HOME/data" \
  "$APP_NEO4J_HOME/logs" \
  "$APP_NEO4J_HOME/plugins" \
  "$APP_NEO4J_HOME/import" \
  "$APP_NEO4J_HOME/certificates" \
  "$APP_NEO4J_HOME/licenses" \
  "$APP_NEO4J_HOME/run"

command_name="${1:-status}"
shift || true

case "$command_name" in
  console)
    exec neo4j console "$@"
    ;;
  start)
    neo4j start "$@"
    ;;
  stop)
    neo4j stop "$@" || true
    ;;
  restart)
    neo4j restart "$@"
    ;;
  status)
    neo4j status "$@" || true
    ;;
  version)
    neo4j version "$@"
    ;;
  *)
    exec neo4j "$command_name" "$@"
    ;;
esac
