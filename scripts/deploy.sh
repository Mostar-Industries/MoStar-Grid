#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — DEPLOYMENT SYNC (RSYNC)
# ═══════════════════════════════════════════════════════════════════

SOURCE_DIR="/home/idona/MoStar/MoStar-Grid"
TARGET_DIR="/opt/mostar/mostar-grid"

echo "🔄 Syncing MoStar Grid Workbench to Deployment..."

# Create target directories
mkdir -p "$TARGET_DIR"

# Sync files, excluding runtime state and git
rsync -avz --progress \
    --exclude '.git' \
    --exclude '.venv*' \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude 'logs/*.log' \
    --exclude 'data/voice_cache/*' \
    --exclude 'backend/neo4j-mostar-industries/data/*' \
    "$SOURCE_DIR/" "$TARGET_DIR/"

echo "✅ Sync complete: $TARGET_DIR"
echo "👉 Use 'scripts/run-*.sh' to start services from the deployment folder."
