#!/bin/bash
set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
BUCKET_NAME="rag-powered-ai-assistant-frontend"
REGION="eu-central-1"
HTML_FILE="$PROJECT_ROOT/frontend/index.html"

echo -e "${BLUE}Deploying frontend to S3...${NC}"

# Verify file exists
if [ ! -f "$HTML_FILE" ]; then
    echo "Error: index.html not found at $HTML_FILE"
    exit 1
fi

# Upload to S3
aws s3 cp "$HTML_FILE" "s3://$BUCKET_NAME/index.html" \
    --region "$REGION" \
    --content-type "text/html" \
    --cache-control "max-age=300"

echo -e "${GREEN}✓ Frontend deployed successfully${NC}"
echo ""
echo "Access URLs:"
echo "  HTTPS: https://$BUCKET_NAME.s3.$REGION.amazonaws.com/index.html"
echo "  HTTP:  http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"