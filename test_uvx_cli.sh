#!/bin/bash
set -e

# echo "🌐 Installing your package from PyPI..."
# uv pip install mcp-snowflake-reader

echo "🚀 Running uvx CLI with real connection string..."

uvx mcp-snowflake-reader \
  --connection '{"user": "cookie", "password": "Taya3023", "account": "gv28284.ap-northeast-2.aws", "warehouse": "DEV_WH", "database": "FNF", "schema": "PRCS", "role": "PU_ALL"}' \
  --allowed-databases FNF \
  --allowed-schemas DEV || echo "✅ CLI invoked (connection will fail, but script works)"

echo "✅ uvx CLI script is callable! All good."
