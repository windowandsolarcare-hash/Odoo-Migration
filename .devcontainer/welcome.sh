#!/bin/bash
echo ""
echo "================================================"
echo "  Window & Solar Care - Odoo Migration"
echo "================================================"
echo ""

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "  ⚠️  ANTHROPIC_API_KEY not set."
  echo ""
  echo "  To fix this once and for all:"
  echo "  1. Go to: https://console.anthropic.com/settings/api-keys"
  echo "  2. Create a key"
  echo "  3. Go to: https://github.com/settings/codespaces"
  echo "     -> New secret -> Name: ANTHROPIC_API_KEY -> paste key"
  echo "     -> Select repo: windowandsolarcare-hash/Odoo-Migration"
  echo "  4. Rebuild this Codespace (it will auto-load next time)"
  echo ""
  echo "  Or for this session only, run:"
  echo "  export ANTHROPIC_API_KEY=sk-ant-..."
  echo ""
else
  echo "  ✅ Claude Code is ready. Type: claude"
  echo ""
fi
echo "================================================"
echo ""
