#!/usr/bin/env bash
# ============================================================
# Test Execution CLI Helper
# ============================================================
#
# Convenience script for running tests with common configurations.
#
# Usage:
#   ./scripts/run_tests.sh smoke          # Run smoke tests
#   ./scripts/run_tests.sh regression     # Run regression suite
#   ./scripts/run_tests.sh e2e            # Run all E2E tests
#   ./scripts/run_tests.sh unit           # Run unit tests
#   ./scripts/run_tests.sh integration    # Run integration tests
#   ./scripts/run_tests.sh all            # Run everything
#   ./scripts/run_tests.sh docker-smoke   # Run smoke in Docker
#   ./scripts/run_tests.sh allure-open    # Open Allure report
#
# ============================================================

set -euo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALLURE_RESULTS="$PROJECT_ROOT/data/allure-results"
BROWSER="${TEST_BROWSER:-chromium}"
BASE_URL="${TEST_BASE_URL:-http://localhost:3000}"

# --- Colors ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${GREEN}[RUN]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
header() { echo -e "\n${CYAN}════════════════════════════════════════${NC}"; echo -e "${CYAN} $1${NC}"; echo -e "${CYAN}════════════════════════════════════════${NC}\n"; }

# --- Ensure allure results directory exists ---
mkdir -p "$ALLURE_RESULTS"

# --- Command dispatch ---
COMMAND="${1:-help}"

case "$COMMAND" in
    smoke)
        header "Running Smoke Tests"
        info "Browser: $BROWSER | Base URL: $BASE_URL"
        cd "$PROJECT_ROOT"
        python -m pytest tests/e2e/ \
            -m smoke \
            --alluredir="$ALLURE_RESULTS" \
            --base-url="$BASE_URL" \
            --browser-name="$BROWSER" \
            -v --tb=short
        ;;

    regression)
        header "Running Regression Suite"
        info "Browser: $BROWSER | Base URL: $BASE_URL"
        cd "$PROJECT_ROOT"
        python -m pytest tests/e2e/ \
            -m regression \
            --alluredir="$ALLURE_RESULTS" \
            --base-url="$BASE_URL" \
            --browser-name="$BROWSER" \
            -v --tb=short
        ;;

    e2e)
        header "Running All E2E Tests"
        info "Browser: $BROWSER | Base URL: $BASE_URL"
        cd "$PROJECT_ROOT"
        python -m pytest tests/e2e/ \
            --alluredir="$ALLURE_RESULTS" \
            --base-url="$BASE_URL" \
            --browser-name="$BROWSER" \
            -v --tb=short
        ;;

    unit)
        header "Running Unit Tests"
        cd "$PROJECT_ROOT"
        python -m pytest tests/unit/ \
            -m unit \
            --alluredir="$ALLURE_RESULTS" \
            -v --tb=short
        ;;

    integration)
        header "Running Integration Tests"
        cd "$PROJECT_ROOT"
        python -m pytest tests/integration/ \
            -m integration \
            --alluredir="$ALLURE_RESULTS" \
            -v --tb=short
        ;;

    all)
        header "Running All Tests"
        cd "$PROJECT_ROOT"
        python -m pytest tests/ \
            --alluredir="$ALLURE_RESULTS" \
            -v --tb=short
        ;;

    docker-smoke)
        header "Running Smoke Tests in Docker"
        cd "$PROJECT_ROOT"
        docker-compose run --rm playwright \
            python -m pytest tests/e2e/ -m smoke \
            --alluredir=data/allure-results \
            -v --tb=short
        ;;

    docker-regression)
        header "Running Regression in Docker"
        cd "$PROJECT_ROOT"
        docker-compose run --rm playwright \
            python -m pytest tests/e2e/ -m regression \
            --alluredir=data/allure-results \
            -v --tb=short
        ;;

    allure-open)
        header "Opening Allure Report"
        if command -v allure >/dev/null 2>&1; then
            allure serve "$ALLURE_RESULTS"
        else
            warn "Allure CLI not installed locally."
            info "Access the Allure Docker dashboard at: http://localhost:5050"
            info "Or install allure: brew install allure (macOS)"
        fi
        ;;

    allure-generate)
        header "Generating Static Allure Report"
        if command -v allure >/dev/null 2>&1; then
            allure generate "$ALLURE_RESULTS" -o "$PROJECT_ROOT/data/allure-report" --clean
            info "Report generated at: $PROJECT_ROOT/data/allure-report/index.html"
        else
            warn "Allure CLI not installed. Use 'allure-open' or Docker dashboard instead."
        fi
        ;;

    clean)
        header "Cleaning Test Artifacts"
        rm -rf "$ALLURE_RESULTS"/*.json "$ALLURE_RESULTS"/*.xml "$ALLURE_RESULTS"/*.png
        info "Allure results cleaned."
        ;;

    help|*)
        echo ""
        echo "QA Automation Agent - Test Runner"
        echo ""
        echo "Usage: ./scripts/run_tests.sh <command>"
        echo ""
        echo "Commands:"
        echo "  smoke             Run smoke tests (fast, critical path)"
        echo "  regression        Run regression suite (comprehensive)"
        echo "  e2e               Run all E2E browser tests"
        echo "  unit              Run unit tests"
        echo "  integration       Run integration tests"
        echo "  all               Run all test suites"
        echo "  docker-smoke      Run smoke tests in Docker container"
        echo "  docker-regression Run regression in Docker container"
        echo "  allure-open       Open Allure report in browser"
        echo "  allure-generate   Generate static Allure HTML report"
        echo "  clean             Remove test result artifacts"
        echo "  help              Show this help message"
        echo ""
        echo "Environment:"
        echo "  TEST_BASE_URL     Target app URL (default: http://localhost:3000)"
        echo "  TEST_BROWSER      Browser engine (default: chromium)"
        echo ""
        ;;
esac
