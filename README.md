# MCP Snowflake Reader

[English](#english) | [한국어](#korean)

## English

A read-only MCP server for Snowflake databases. This server provides secure, read-only access to Snowflake databases through the MCP protocol.

### Features

- Read-only access to Snowflake databases
- Secure connection handling
- Access control for databases, schemas, and tables
- Docker support
- MCP protocol compliance

### Prerequisites

- Python 3.10 or higher
- Docker (optional)
- Snowflake account with appropriate permissions

### Installation

```bash
# Clone the repository
git clone https://github.com/fnf-deepHeading/mcp-snowflake-reader.git
cd mcp-snowflake-reader

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Running with Docker

```bash
# Build the Docker image
docker build -t mcp-snowflake-reader .

# Run with connection details
docker run mcp-snowflake-reader --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}'

# Run with access control
docker run mcp-snowflake-reader --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}' --allowed-databases DB1 DB2 --allowed-schemas SCHEMA1 SCHEMA2 --allowed-tables TABLE1 TABLE2

# Show help
docker run mcp-snowflake-reader -h
```

#### Running directly

```bash
# Run with connection details
python main.py --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}'

# Run with access control
python main.py --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}' --allowed-databases DB1 DB2 --allowed-schemas SCHEMA1 SCHEMA2 --allowed-tables TABLE1 TABLE2

# Show help
python main.py -h
```

### Command Line Options

- `--connection`: Snowflake 연결 정보 (JSON 문자열)
- `--allowed-databases`: 허용할 데이터베이스 목록 (선택사항)
- `--allowed-schemas`: 허용할 스키마 목록 (선택사항)
- `--allowed-tables`: 허용할 테이블 목록 (선택사항)
- `-h, --help`: 도움말 표시

### API Endpoints

- `snowflake://tables`: 접근 가능한 모든 테이블 목록 조회
- `snowflake://schema/{table_name}`: 특정 테이블의 스키마 조회
- `query`: 읽기 전용 쿼리 실행

### Security

- Read-only access only
- Access control at database, schema, and table levels
- Secure connection handling
- No write operations allowed

## Korean

Snowflake 데이터베이스에 대한 읽기 전용 MCP 서버입니다. 이 서버는 MCP 프로토콜을 통해 Snowflake 데이터베이스에 대한 안전한 읽기 전용 접근을 제공합니다.

### 주요 기능

- Snowflake 데이터베이스 읽기 전용 접근
- 안전한 연결 처리
- 데이터베이스, 스키마, 테이블 수준의 접근 제어
- Docker 지원
- MCP 프로토콜 준수

### 사전 요구사항

- Python 3.10 이상
- Docker (선택사항)
- 적절한 권한이 있는 Snowflake 계정

### 설치 방법

```bash
# 저장소 클론
git clone https://github.com/fnf-deepHeading/mcp-snowflake-reader.git
cd mcp-snowflake-reader

# 의존성 설치
pip install -r requirements.txt
```

### 사용 방법

#### Docker로 실행

```bash
# Docker 이미지 빌드
docker build -t mcp-snowflake-reader .

# 연결 정보로 실행
docker run mcp-snowflake-reader --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}'

# 접근 제어와 함께 실행
docker run mcp-snowflake-reader --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}' --allowed-databases DB1 DB2 --allowed-schemas SCHEMA1 SCHEMA2 --allowed-tables TABLE1 TABLE2

# 도움말 표시
docker run mcp-snowflake-reader -h
```

#### 직접 실행

```bash
# 연결 정보로 실행
python main.py --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}'

# 접근 제어와 함께 실행
python main.py --connection '{"account":"USER_ACCOUNT.ap-northeast-2.aws","user":"USER_NAME","password":"USER_PASSWORD","warehouse":"USER_WAREHOUSE","database":"USER_DATABASE","role":"USER_ROLE","port":"443"}' --allowed-databases DB1 DB2 --allowed-schemas SCHEMA1 SCHEMA2 --allowed-tables TABLE1 TABLE2

# 도움말 표시
python main.py -h
```

### 명령줄 옵션

- `--connection`: Snowflake 연결 정보 (JSON 문자열)
- `--allowed-databases`: 허용할 데이터베이스 목록 (선택사항)
- `--allowed-schemas`: 허용할 스키마 목록 (선택사항)
- `--allowed-tables`: 허용할 테이블 목록 (선택사항)
- `-h, --help`: 도움말 표시

### API 엔드포인트

- `snowflake://tables`: 접근 가능한 모든 테이블 목록 조회
- `snowflake://schema/{table_name}`: 특정 테이블의 스키마 조회
- `query`: 읽기 전용 쿼리 실행

### 보안

- 읽기 전용 접근만 허용
- 데이터베이스, 스키마, 테이블 수준의 접근 제어
- 안전한 연결 처리
- 쓰기 작업 불가

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