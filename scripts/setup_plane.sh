#!/usr/bin/env bash
# ============================================================
# Plane.so Initial Setup & Webhook Registration
# ============================================================
#
# This script provisions a Plane.so workspace and project for the
# QA Automation Agent, creates required states, and registers the
# webhook endpoint.
#
# Prerequisites:
#   - Plane.so is running (docker-compose up plane-web plane-api)
#   - PLANE_BASE_URL, PLANE_API_KEY set in .env or environment
#   - curl and jq installed
#
# Usage:
#   chmod +x scripts/setup_plane.sh
#   source .env && ./scripts/setup_plane.sh
#
# ============================================================

set -euo pipefail

# --- Configuration ---
PLANE_BASE_URL="${PLANE_BASE_URL:-http://localhost:8080}"
PLANE_API_KEY="${PLANE_API_KEY:-}"
WORKSPACE_SLUG="${PLANE_WORKSPACE_SLUG:-qa-automation}"
PROJECT_NAME="QA Test Board"
WEBHOOK_URL="${WEBHOOK_URL:-http://app:8000/webhooks/plane}"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Validation ---
if [ -z "$PLANE_API_KEY" ]; then
    error "PLANE_API_KEY is not set. Please set it in .env or export it."
fi

command -v curl >/dev/null 2>&1 || error "curl is required but not installed."
command -v jq >/dev/null 2>&1 || error "jq is required but not installed."

info "Setting up Plane.so at: $PLANE_BASE_URL"
info "Workspace: $WORKSPACE_SLUG"

HEADERS=(-H "X-API-Key: $PLANE_API_KEY" -H "Content-Type: application/json")

# --- Step 1: Verify API connectivity ---
info "Checking Plane.so API connectivity..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    "${HEADERS[@]}" \
    "$PLANE_BASE_URL/api/v1/users/me/")

if [ "$RESPONSE" != "200" ]; then
    error "Cannot connect to Plane.so API (HTTP $RESPONSE). Check PLANE_BASE_URL and PLANE_API_KEY."
fi
info "API connection successful."

# --- Step 2: Create or find workspace ---
info "Looking for workspace: $WORKSPACE_SLUG..."
WORKSPACE_EXISTS=$(curl -s "${HEADERS[@]}" \
    "$PLANE_BASE_URL/api/v1/workspaces/$WORKSPACE_SLUG/" \
    | jq -r '.slug // empty')

if [ -z "$WORKSPACE_EXISTS" ]; then
    info "Creating workspace: $WORKSPACE_SLUG..."
    curl -s "${HEADERS[@]}" \
        -X POST "$PLANE_BASE_URL/api/v1/workspaces/" \
        -d "{\"name\": \"QA Automation\", \"slug\": \"$WORKSPACE_SLUG\"}" \
        | jq .
    info "Workspace created."
else
    info "Workspace already exists: $WORKSPACE_SLUG"
fi

# --- Step 3: Create project ---
info "Creating project: $PROJECT_NAME..."
PROJECT_RESPONSE=$(curl -s "${HEADERS[@]}" \
    -X POST "$PLANE_BASE_URL/api/v1/workspaces/$WORKSPACE_SLUG/projects/" \
    -d "{\"name\": \"$PROJECT_NAME\", \"identifier\": \"QAT\", \"network\": 2}")

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | jq -r '.id // empty')

if [ -z "$PROJECT_ID" ]; then
    warn "Project may already exist. Trying to fetch it..."
    PROJECT_ID=$(curl -s "${HEADERS[@]}" \
        "$PLANE_BASE_URL/api/v1/workspaces/$WORKSPACE_SLUG/projects/" \
        | jq -r '.results[] | select(.name == "'"$PROJECT_NAME"'") | .id // empty' 2>/dev/null)

    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(curl -s "${HEADERS[@]}" \
            "$PLANE_BASE_URL/api/v1/workspaces/$WORKSPACE_SLUG/projects/" \
            | jq -r '.[0].id // empty' 2>/dev/null)
    fi
fi

if [ -z "$PROJECT_ID" ]; then
    error "Failed to create or find project."
fi

info "Project ID: $PROJECT_ID"

# --- Step 4: Create issue states ---
info "Creating issue states for QA workflow..."

create_state() {
    local name="$1"
    local group="$2"
    local color="$3"

    curl -s "${HEADERS[@]}" \
        -X POST "$PLANE_BASE_URL/api/v1/workspaces/$WORKSPACE_SLUG/projects/$PROJECT_ID/states/" \
        -d "{\"name\": \"$name\", \"group\": \"$group\", \"color\": \"$color\"}" \
        > /dev/null 2>&1 || true

    info "  State: $name ($group)"
}

create_state "TODO" "backlog" "#a3a3a3"
create_state "DOING" "started" "#f59e0b"
create_state "FINISHED" "completed" "#22c55e"
create_state "FAILED" "cancelled" "#ef4444"

# --- Step 5: Register webhook ---
info "Registering webhook: $WEBHOOK_URL..."
WEBHOOK_RESPONSE=$(curl -s "${HEADERS[@]}" \
    -X POST "$PLANE_BASE_URL/api/v1/workspaces/$WORKSPACE_SLUG/webhooks/" \
    -d "{
        \"url\": \"$WEBHOOK_URL\",
        \"is_active\": true,
        \"issue\": true,
        \"issue_comment\": false,
        \"project\": false,
        \"cycle\": false,
        \"module\": false
    }" 2>/dev/null)

WEBHOOK_ID=$(echo "$WEBHOOK_RESPONSE" | jq -r '.id // empty')
WEBHOOK_SECRET=$(echo "$WEBHOOK_RESPONSE" | jq -r '.secret_key // empty')

if [ -n "$WEBHOOK_ID" ]; then
    info "Webhook registered successfully."
    info "  Webhook ID: $WEBHOOK_ID"
    if [ -n "$WEBHOOK_SECRET" ]; then
        warn "  Webhook Secret: $WEBHOOK_SECRET"
        warn "  Add this to your .env as: PLANE_WEBHOOK_SECRET=$WEBHOOK_SECRET"
    fi
else
    warn "Webhook registration returned no ID (may already exist)."
fi

# --- Summary ---
echo ""
echo "============================================================"
info "Setup complete!"
echo "============================================================"
echo ""
echo "Add these values to your .env file:"
echo ""
echo "  PLANE_BASE_URL=$PLANE_BASE_URL"
echo "  PLANE_WORKSPACE_SLUG=$WORKSPACE_SLUG"
echo "  PLANE_PROJECT_ID=$PROJECT_ID"
if [ -n "$WEBHOOK_SECRET" ]; then
    echo "  PLANE_WEBHOOK_SECRET=$WEBHOOK_SECRET"
fi
echo ""
echo "============================================================"
echo ""
echo "WEBHOOK REGISTRATION (Manual steps if automatic failed):"
echo ""
echo "1. Open Plane.so: $PLANE_BASE_URL"
echo "2. Go to: Workspace Settings → Webhooks"
echo "3. Click 'Add Webhook'"
echo "4. Set URL to: $WEBHOOK_URL"
echo "5. Enable events: Issues (state changes)"
echo "6. Copy the generated secret to .env as PLANE_WEBHOOK_SECRET"
echo "7. Save the webhook"
echo ""
echo "============================================================"
