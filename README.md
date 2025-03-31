# Snowflake Read Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Snowflake 데이터베이스에 연결하여 테이블 스키마를 조회하고 쿼리를 실행할 수 있는 MCP(Model Context Protocol) 서버입니다.

## 설치 방법

1. Python 3.10 이상이 필요합니다.
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 사용 방법

### 로컬 실행

1. Snowflake 연결 정보를 JSON 형식으로 준비합니다:
   ```json
   {
     "account": "your_account",
     "user": "your_username",
     "password": "your_password",
     "warehouse": "your_warehouse",
     "database": "your_database",
     "schema": "your_schema"
   }
   ```

2. 서버 실행:
   ```bash
   python main.py '{"account": "your_account", "user": "your_username", ...}'
   ```

### 도커 실행

1. 도커 이미지 빌드:
   ```bash
   docker build -t snowflake-read-python .
   ```

2. 도커 컨테이너 실행:
   ```bash
   # 연결 정보를 환경 변수로 전달
   docker run -e SNOWFLAKE_CONNECTION='{"account": "your_account", "user": "your_username", "password": "your_password", "warehouse": "your_warehouse", "database": "your_database", "schema": "your_schema"}' snowflake-read-python

   # 또는 파일에서 연결 정보 읽기
   docker run -v $(pwd)/connection.json:/app/connection.json snowflake-read-python "$(cat /app/connection.json)"
   ```

## 지원하는 기능

1. 테이블 목록 조회
2. 테이블 스키마 조회
3. SQL 쿼리 실행 (읽기 전용)

## 에러 처리

- 모든 에러는 표준 에러(stderr)로 출력됩니다.
- 연결 실패, 쿼리 실행 오류 등이 발생하면 적절한 에러 메시지가 표시됩니다.

## 보안 주의사항

- 연결 정보에 민감한 데이터가 포함되어 있으므로 안전하게 관리해야 합니다.
- 환경 변수나 설정 파일을 통해 연결 정보를 관리하는 것을 권장합니다.
- 도커 환경에서 실행할 때는 연결 정보를 환경 변수나 마운트된 설정 파일을 통해 전달하는 것이 좋습니다. 