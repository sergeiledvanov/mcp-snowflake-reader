# MCP Snowflake Reader

[English](#english) | [한국어](#korean)

## English

A read-only MCP server for Snowflake databases. This server provides secure, read-only access to Snowflake databases through the MCP protocol.

### Features

- **Read-only Access**: Secure read-only access to Snowflake databases
- **Access Control**: Fine-grained access control at database, schema, and table levels

### Setup

#### Snowflake Connection

The Snowflake connection information should be provided as a JSON string in the following format:

```json
{
  "account": "your-account",
  "user": "your-user",
  "password": "your-password",
  "warehouse": "your-warehouse",
  "database": "your-database",
  "schema": "your-schema",
  "role": "your-role"
}
```

#### MCP Client Configuration

Add the following configuration to your MCP client settings file (Cursor AI or Claude):

##### Docker

```json
{
  "mcpServers": {
    "mcp-snowflake-reader": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "mcp-snowflake-reader",
        "--connection",
        "{\"account\":\"your-account\",\"user\":\"your-user\",\"password\":\"your-password\",\"warehouse\":\"your-warehouse\",\"database\":\"your-database\",\"schema\":\"your-schema\",\"role\":\"your-role\"}"
      ]
    }
  }
}
```

##### UVX

```json
{
  "mcpServers": {
    "mcp-snowflake-reader": {
      "command": "uvx",
      "args": [
        "mcp-snowflake-reader",
        "--connection",
        "{\"account\":\"your-account\",\"user\":\"your-user\",\"password\":\"your-password\",\"warehouse\":\"your-warehouse\",\"database\":\"your-database\",\"schema\":\"your-schema\",\"role\":\"your-role\"}"
      ]
    }
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
- When access control is enabled, only allowed databases, schemas, and tables are accessible

## Korean

Snowflake 데이터베이스의 테이블을 읽어오는 MCP(Microservice Control Protocol) 서버입니다.

### 주요 기능

- **읽기 전용 접근**: Snowflake 데이터베이스에 대한 안전한 읽기 전용 접근
- **접근 제어**: 데이터베이스, 스키마, 테이블 수준의 세밀한 접근 제어

### 설정

#### Snowflake 연결 정보

Snowflake 연결 정보는 다음과 같은 형식으로 JSON 문자열로 제공됩니다:

```json
{
  "account": "your-account",
  "user": "your-user",
  "password": "your-password",
  "warehouse": "your-warehouse",
  "database": "your-database",
  "schema": "your-schema",
  "role": "your-role"
}
```

#### MCP 클라이언트 설정

Cursor AI나 Claude와 같은 MCP 클라이언트의 설정 파일에 다음 설정을 추가하세요:

##### Docker

```json
{
  "mcpServers": {
    "mcp-snowflake-reader": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "mcp-snowflake-reader",
        "--connection",
        "{\"account\":\"your-account\",\"user\":\"your-user\",\"password\":\"your-password\",\"warehouse\":\"your-warehouse\",\"database\":\"your-database\",\"schema\":\"your-schema\",\"role\":\"your-role\"}"
      ]
    }
  }
}
```

##### UVX

```json
{
  "mcpServers": {
    "mcp-snowflake-reader": {
      "command": "uvx",
      "args": [
        "mcp-snowflake-reader",
        "--connection",
        "{\"account\":\"your-account\",\"user\":\"your-user\",\"password\":\"your-password\",\"warehouse\":\"your-warehouse\",\"database\":\"your-database\",\"schema\":\"your-schema\",\"role\":\"your-role\"}"
      ]
    }
  }
}
```



### 제한사항

- 읽기 전용 작업만 허용됩니다
- 테이블 이름은 영숫자, 언더스코어, 점만 허용됩니다
- 다음 SQL 키워드는 금지됩니다:
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
- 접근 제어가 설정된 경우, 허용된 데이터베이스, 스키마, 테이블만 접근 가능합니다

## License

MIT License 