#!/usr/bin/env python3

import json
import sys
import re
import argparse
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Set

import snowflake.connector
from mcp.server.fastmcp import FastMCP


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='MCP server for read-only access to Snowflake databases')
    parser.add_argument('--connection', required=True, help='Snowflake connection details as JSON string')
    
    args = parser.parse_args()
    return args


def validate_table_name(table_name: str) -> bool:
    """Validates table name to prevent SQL injection.
    Args:
        table_name: Name of the table to validate
    Returns:
        bool: True if table name is valid, False otherwise
    """
    # Allow only alphanumeric characters, underscores, and dots
    pattern = r'^[a-zA-Z0-9_\.]+$'
    return bool(re.match(pattern, table_name))


def validate_sql_query(sql: str) -> bool:
    """Validates SQL query to ensure it's read-only.
    Args:
        sql: SQL query to validate
    Returns:
        bool: True if query is read-only, False otherwise
    """
    # List of forbidden SQL keywords
    forbidden_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER',
        'CREATE', 'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK'
    ]
    
    # Convert to uppercase for case-insensitive matching
    sql_upper = sql.upper()
    return not any(keyword in sql_upper for keyword in forbidden_keywords)


@asynccontextmanager
async def app_lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    """Manages Snowflake connection lifecycle during server startup/shutdown.
    Establishes connection when server starts and ensures proper cleanup on shutdown."""
    args = parse_args()
    try:
        connection_details = json.loads(args.connection)
        mcp.connection = snowflake.connector.connect(**connection_details)
        mcp.is_connected = True
        yield
    except json.JSONDecodeError:
        raise Exception("연결 정보가 올바른 JSON 형식이 아닙니다. JSON 형식을 확인해주세요.")
    except snowflake.connector.errors.InterfaceError as e:
        if "404 Not Found" in str(e):
            raise Exception("Snowflake 서버에 연결할 수 없습니다. 계정 정보를 확인해주세요.")
        elif "250001" in str(e):
            raise Exception("사용자 이름 또는 비밀번호가 올바르지 않습니다.")
        else:
            raise Exception(f"Snowflake 연결 오류: {str(e)}")
    except Exception as e:
        raise Exception(f"Snowflake 연결 실패: {str(e)}\n연결 정보를 다시 확인해주세요.")
    finally:
        if hasattr(mcp, 'connection') and mcp.connection:
            mcp.connection.close()
            mcp.is_connected = False


# Create FastMCP instance with lifespan function for connection management
mcp = FastMCP("snowflake-read", lifespan=app_lifespan)


@mcp.resource("snowflake://tables")
def list_tables() -> str:
    """Returns a list of all tables in the connected Snowflake database.
    The result is formatted as a JSON string containing table information."""
    if not mcp.connection or not mcp.is_connected:
        raise Exception("Not connected to Snowflake")

    cursor = mcp.connection.cursor()
    try:
        cursor.execute("SHOW TABLES")
        rows = cursor.fetchall()
        return json.dumps(rows, default=str, indent=2)
    except Exception as e:
        raise Exception(f"Failed to list tables: {str(e)}")
    finally:
        cursor.close()


@mcp.resource("snowflake://schema/{table_name}")
def get_table_schema(table_name: str) -> str:
    """Retrieves and returns the schema information for a specific table.
    Args:
        table_name: Name of the table to describe
    Returns:
        JSON string containing column definitions and other table metadata"""
    if not mcp.connection or not mcp.is_connected:
        raise Exception("Not connected to Snowflake")
    
    if not validate_table_name(table_name):
        raise ValueError("Invalid table name")

    cursor = mcp.connection.cursor()
    try:
        cursor.execute(f"DESCRIBE TABLE {table_name}")
        rows = cursor.fetchall()
        return json.dumps(rows, default=str, indent=2)
    except Exception as e:
        raise Exception(f"Failed to get table schema: {str(e)}")
    finally:
        cursor.close()


@mcp.tool()
def query(sql: str) -> str:
    """Executes a read-only SQL query against the Snowflake database.
    Args:
        sql: SQL query string to execute (must be read-only)
    Returns:
        Query results as a JSON-formatted string
    Note: 
        This function is restricted to read-only operations for security"""
    if not mcp.connection or not mcp.is_connected:
        raise Exception("Not connected to Snowflake")
    
    if not validate_sql_query(sql):
        raise ValueError("Query contains forbidden keywords or is not read-only")

    cursor = mcp.connection.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return json.dumps(rows, default=str, indent=2)
    except Exception as e:
        raise Exception(f"Failed to execute query: {str(e)}")
    finally:
        cursor.close()


def main():
    """Entry point for the MCP server."""
    try:
        # 도움말 출력 여부 확인
        if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
            parse_args()
            return
            
        mcp.run()
    except KeyboardInterrupt:
        print("\n👋 MCP Snowflake Reader stopped by user.")


if __name__ == "__main__":
    main()