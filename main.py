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
    parser.add_argument('--allowed-databases', nargs='*', help='List of allowed databases')
    parser.add_argument('--allowed-schemas', nargs='*', help='List of allowed schemas')
    parser.add_argument('--allowed-tables', nargs='*', help='List of allowed tables')
    
    # 도움말 출력 후 바로 종료
    if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
        parser.print_help()
        sys.exit(0)
    
    return parser.parse_args()


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


def check_access_permission(database: str, schema: str, table: str, allowed_databases: Set[str], allowed_schemas: Set[str], allowed_tables: Set[str]) -> bool:
    """Check if access to the specified database, schema, and table is allowed.
    Args:
        database: Database name
        schema: Schema name
        table: Table name
        allowed_databases: Set of allowed database names
        allowed_schemas: Set of allowed schema names
        allowed_tables: Set of allowed table names
    Returns:
        bool: True if access is allowed, False otherwise
    """
    # If no restrictions are set, allow all access
    if not (allowed_databases or allowed_schemas or allowed_tables):
        return True

    # Check database access
    if allowed_databases and database not in allowed_databases:
        return False

    # Check schema access
    if allowed_schemas and schema not in allowed_schemas:
        return False

    # Check table access
    if allowed_tables and table not in allowed_tables:
        return False

    return True


@asynccontextmanager
async def app_lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    """Manages Snowflake connection lifecycle during server startup/shutdown.
    Establishes connection when server starts and ensures proper cleanup on shutdown."""
    args = parse_args()
    try:
        connection_details = json.loads(args.connection)
        mcp.connection = snowflake.connector.connect(**connection_details)
        mcp.is_connected = True
        mcp.allowed_databases = set(args.allowed_databases or [])
        mcp.allowed_schemas = set(args.allowed_schemas or [])
        mcp.allowed_tables = set(args.allowed_tables or [])
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
        
        # Filter tables based on access permissions
        if mcp.allowed_databases or mcp.allowed_schemas or mcp.allowed_tables:
            filtered_rows = []
            for row in rows:
                database = row[1]  # database_name
                schema = row[2]    # schema_name
                table = row[3]     # table_name
                if check_access_permission(database, schema, table, mcp.allowed_databases, mcp.allowed_schemas, mcp.allowed_tables):
                    filtered_rows.append(row)
            return json.dumps(filtered_rows, default=str, indent=2)
        
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
        # Get database and schema for the table
        cursor.execute(f"SELECT DATABASE_NAME, SCHEMA_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Table {table_name} not found")
        
        database, schema = result
        if not check_access_permission(database, schema, table_name, mcp.allowed_databases, mcp.allowed_schemas, mcp.allowed_tables):
            raise ValueError(f"Access to table {table_name} is not allowed")

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
        # Extract table names from the query
        table_pattern = r'FROM\s+([a-zA-Z0-9_\.]+)'
        tables = re.findall(table_pattern, sql, re.IGNORECASE)
        
        # Check access permissions for each table
        for table in tables:
            parts = table.split('.')
            if len(parts) == 3:
                database, schema, table_name = parts
            elif len(parts) == 2:
                schema, table_name = parts
                database = mcp.connection.database
            else:
                table_name = parts[0]
                database = mcp.connection.database
                schema = mcp.connection.schema

            if not check_access_permission(database, schema, table_name, mcp.allowed_databases, mcp.allowed_schemas, mcp.allowed_tables):
                raise ValueError(f"Access to table {table} is not allowed")

        cursor.execute(sql)
        rows = cursor.fetchall()
        return json.dumps(rows, default=str, indent=2)
    except Exception as e:
        raise Exception(f"Failed to execute query: {str(e)}")
    finally:
        cursor.close()


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()