## English

A read-only MCP server for Snowflake databases. This server provides secure, read-only access to Snowflake databases through the MCP protocol.

### Features

- **Read-only Access**: Secure read-only access to Snowflake databases

### Setup

#### Snowflake Connection

The Snowflake connection information should be provided as an .env file in the following format:

```.env
SNOWFLAKE_AUTH_TYPE=externalbrowser
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_DATABASE=...
SNOWFLAKE_WAREHOUSE=...
```

#### MCP Client Configuration

Add the following configuration to your MCP client settings file (Cursor AI or Claude):

##### Docker

```json
  "mcpServers": {
    "sf-reader": {
      "command": "/path/to/mcp-snowflake-reader/.venv/bin/python",
      "args": [
        "-m",
        "mcp_snowflake_reader.main"
      ],
      "cwd": "/path/to/mcp-snowflake-reader"
    }
  }
```

### Limitations

- Only read-only operations are allowed
- Table names can only contain alphanumeric characters, underscores, and dots
- The following SQL keywords are prohibited:
  - INSERT
  - UPDATE
  - DELETE
  - DROP
  - TRUNCATE
  - ALTER
  - CREATE
  - GRANT
  - REVOKE
  - COMMIT
  - ROLLBACK

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
