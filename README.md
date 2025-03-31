# MCP Snowflake Reader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Snowflake 데이터베이스에 대한 읽기 전용 접근을 제공하는 MCP 서버입니다.

## 기능

- 테이블 목록 조회
- 테이블 스키마 조회
- 읽기 전용 SQL 쿼리 실행
- 데이터베이스, 스키마, 테이블 수준의 접근 제어

## 보안

이 서버는 읽기 전용 작업만 허용하며, 다음과 같은 보안 기능을 제공합니다:

- SQL 인젝션 방지를 위한 테이블 이름 검증
- 읽기 전용 쿼리만 허용 (INSERT, UPDATE, DELETE 등 금지)
- 데이터베이스, 스키마, 테이블 수준의 세분화된 접근 제어

## 설치

```bash
pip install mcp-snowflake-reader
```

## 사용법

### Docker로 실행

```bash
docker build -t mcp-snowflake-reader .
docker run -e MCP_SNOWFLAKE_CONNECTION='{"account":"USER_ACCOUNT","port":"443","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE"}' mcp-snowflake-reader
```

### 직접 실행

```bash
python main.py --connection '{"account":"USER_ACCOUNT","port":"443","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE"}'
```

## API 엔드포인트

### 테이블 목록 조회
```
GET /snowflake://tables
```

### 테이블 스키마 조회
```
GET /snowflake://schema/{table_name}
```

### SQL 쿼리 실행
```
POST /query
Content-Type: application/json

{
    "sql": "SELECT * FROM your_table LIMIT 10"
}
```

## 제한사항

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

## 라이선스

MIT License 