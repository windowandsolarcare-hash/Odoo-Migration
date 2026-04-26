#!/bin/bash
# GitHub File Deployment Script
# Purpose: Reliable file deployment to GitHub via gh CLI
# Usage: ./deploy_to_github.sh <repo> <file_path> <local_file> <commit_message>
# Example: ./deploy_to_github.sh windowandsolarcare-hash/Odoo-Migration 1_Production_Code/phase3.py /path/to/phase3.py "2026-04-26 | phase3.py | fixed bug"

set -e

REPO=$1
FILE_PATH=$2
LOCAL_FILE=$3
COMMIT_MSG=$4

# Validate inputs
if [[ -z "$REPO" || -z "$FILE_PATH" || -z "$LOCAL_FILE" || -z "$COMMIT_MSG" ]]; then
    echo "❌ Missing arguments"
    echo "Usage: $0 <repo> <file_path> <local_file> <commit_message>"
    echo "Example: $0 windowandsolarcare-hash/Odoo-Migration 1_Production_Code/phase3.py ./phase3.py '2026-04-26 | phase3.py | description'"
    exit 1
fi

if [[ ! -f "$LOCAL_FILE" ]]; then
    echo "❌ Local file not found: $LOCAL_FILE"
    exit 1
fi

echo "📤 Deploying to GitHub..."
echo "   Repo: $REPO"
echo "   File: $FILE_PATH"
echo "   Local: $LOCAL_FILE"
echo "   Message: $COMMIT_MSG"

# Get base64 content from local file using PowerShell (handles Windows paths)
base64_content=$(powershell -Command "
\$content = Get-Content '$LOCAL_FILE' -Raw -Encoding UTF8
\$bytes = [System.Text.Encoding]::UTF8.GetBytes(\$content)
\$base64 = [System.Convert]::ToBase64String(\$bytes)
Write-Output \$base64
" 2>/dev/null)

if [[ -z "$base64_content" ]]; then
    echo "❌ Failed to read or encode local file"
    exit 1
fi

# Create JSON payload in temp file
TEMP_PAYLOAD=$(mktemp)
cat > "$TEMP_PAYLOAD" <<EOF
{
  "message": "$COMMIT_MSG",
  "content": "$base64_content",
  "branch": "main"
}
EOF

# Push to GitHub
if gh api "repos/$REPO/contents/$FILE_PATH" --method PUT --input "$TEMP_PAYLOAD"; then
    echo "✅ File deployed successfully"
    rm "$TEMP_PAYLOAD"
    exit 0
else
    echo "❌ GitHub API failed"
    echo "   Payload temp file: $TEMP_PAYLOAD"
    echo "   (temp file left for debugging)"
    exit 1
fi
