# Allure Report Server
# Serves Allure HTML reports from the shared results volume
#
# Build: docker build -f docker/allure/Dockerfile -t qa-agent-allure docker/allure/
# Access: http://localhost:5050

FROM frankescobar/allure-docker-service:latest

# Environment configuration
ENV CHECK_RESULTS_EVERY_SECONDS=5
ENV KEEP_HISTORY=25
ENV KEEP_HISTORY_LATEST=5

# Expose the Allure UI port
EXPOSE 5050

# Results directory is mounted as a volume at runtime
# via docker-compose: ./data/allure-results:/app/allure-results
