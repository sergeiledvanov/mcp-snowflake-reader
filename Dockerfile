FROM python:3.10-slim

WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY main.py .

# 실행 권한 설정
RUN chmod +x main.py

# 환경 변수 설정 (기본값)
ENV MCP_SNOWFLAKE_CONNECTION='{}'
ENV MCP_ALLOWED_DATABASES=''
ENV MCP_ALLOWED_SCHEMAS=''
ENV MCP_ALLOWED_TABLES=''

# 실행 명령
CMD /bin/sh -c 'python main.py --connection "$MCP_SNOWFLAKE_CONNECTION" \
    $([ ! -z "$MCP_ALLOWED_DATABASES" ] && echo "--allowed-databases $MCP_ALLOWED_DATABASES") \
    $([ ! -z "$MCP_ALLOWED_SCHEMAS" ] && echo "--allowed-schemas $MCP_ALLOWED_SCHEMAS") \
    $([ ! -z "$MCP_ALLOWED_TABLES" ] && echo "--allowed-tables $MCP_ALLOWED_TABLES")' 