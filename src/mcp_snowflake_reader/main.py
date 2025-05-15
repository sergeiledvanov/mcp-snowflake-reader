#!/usr/bin/env python3

import json
import re
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Set

import snowflake.connector
import os
import sqlparse

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(filename='mcp-snowflake-reader.log', encoding='utf-8', level=logging.DEBUG)


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
    for keyword in forbidden_keywords:
        # Use word boundaries \b to match whole words only
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, sql_upper):
            return False

    return True


def get_connection():
    """Snowflake 연결을 얻습니다. 연결이 없을 경우 새로 생성합니다."""
    if not hasattr(get_connection, 'connection') or get_connection.connection is None:
        try:
            get_connection.connection = snowflake.connector.connect(**get_connection.connection_details)
        except Exception as e:
            logger.info(f"Exception {str(e)}")
            raise Exception(f"Snowflake 연결 실패: {str(e)}")

    return get_connection.connection


@asynccontextmanager
async def app_lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    """Manages Snowflake connection lifecycle during server startup/shutdown."""

    # Load environment variables from .env file
    load_dotenv()

    try:

        # Get connection details from environment variables
        connection_details = {
            "authenticator": os.environ.get("SNOWFLAKE_AUTH_TYPE"),
            "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
            "user": os.environ.get("SNOWFLAKE_USER"),
            "database": os.environ.get("SNOWFLAKE_DATABASE"),
            "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE")
        }

        # Remove None values
        connection_details = {k: v for k, v in connection_details.items() if v is not None}

        if not connection_details:
            logger.info("No Snowflake connection details found in environment variables")
            raise Exception("No Snowflake connection details found in environment variables")

        logger.info(f"Snowflake connection details loaded from environment variables ${connection_details}")

        # 연결 정보 저장 (실제 연결은 필요할 때만 수행)
        get_connection.connection_details = connection_details
        get_connection.connection = None

        yield
    except json.JSONDecodeError as e:
        logger.info(f"JSONDecodeError {str(e)}")
        raise Exception("연결 정보가 올바른 JSON 형식이 아닙니다. JSON 형식을 확인해주세요.")
    except Exception as e:
        logger.info(f"Exception {str(e)}")
        raise Exception(f"설정 오류: {str(e)}")
    finally:
        # 연결이 있으면 종료
        if hasattr(get_connection, 'connection') and get_connection.connection:
            get_connection.connection.close()
            get_connection.connection = None


# Create FastMCP instance with lifespan function for connection management
mcp = FastMCP("snowflake-read", lifespan=app_lifespan)
logger.info("MCP Snowflake Reader started")

@mcp.resource("snowflake://tables")
def list_tables() -> str:
    """Returns a list of all tables in the connected Snowflake database.
    The result is formatted as a JSON string containing table information."""
    try:
        # 필요할 때만 연결 얻기
        conn = get_connection()

        cursor = conn.cursor()
        try:
            cursor.execute("SHOW TABLES")
            rows = cursor.fetchall()
            return json.dumps(rows, default=str, indent=2)
        except Exception as e:
            logger.info(f"Failed to list tables: {str(e)}")
            raise Exception(f"Failed to list tables: {str(e)}")
        finally:
            cursor.close()
    except Exception as e:
        logger.info(f"Failed to connect to Snowflake: {str(e)}")
        raise Exception(f"Failed to connect to Snowflake: {str(e)}")


@mcp.resource("snowflake://schema/{table_name}")
def get_table_schema(table_name: str) -> str:
    """Retrieves and returns the schema information for a specific table.
    Args:
        table_name: Name of the table to describe
    Returns:
        JSON string containing column definitions and other table metadata"""
    if not validate_table_name(table_name):
        logger.info(f"Invalid table name: {table_name}")
        raise ValueError("Invalid table name")

    try:
        # 필요할 때만 연결 얻기
        conn = get_connection()

        cursor = conn.cursor()
        try:
            cursor.execute(f"DESCRIBE TABLE {table_name}")
            rows = cursor.fetchall()
            return json.dumps(rows, default=str, indent=2)
        except Exception as e:
            logger.info(f"Failed to get table schema: {str(e)}")
            raise Exception(f"Failed to get table schema: {str(e)}")
        finally:
            cursor.close()
    except Exception as e:
        logger.info(f"Failed to connect to Snowflake: {str(e)}")
        raise Exception(f"Failed to connect to Snowflake: {str(e)}")


@mcp.tool()
def query(sql: str) -> str:
    """Executes a read-only SQL query against the Snowflake database.
    Args:
        sql: SQL query string to execute (must be read-only)
    Returns:
        Query results as a formatted table string
    Note:
        This function is restricted to read-only operations for security"""
    if not validate_sql_query(sql):
        logger.info(f"Query contains forbidden keywords: {sql}")
        raise ValueError("Query contains forbidden keywords or is not read-only")

    # Format SQL query for better readability using sqlparse
    formatted_sql = sqlparse.format(sql,
                                  reindent=True,
                                  keyword_case='upper',
                                  indent_width=4)

    # Display formatted query before execution
    logger.info(f"Executing query for: \n{formatted_sql}")

    try:
        # 필요할 때만 연결 얻기
        conn = get_connection()

        cursor = conn.cursor()
        try:
            cursor.execute(sql)

            # Get column names from cursor description
            columns = [col[0] for col in cursor.description] if cursor.description else []

            # Fetch all rows
            rows = cursor.fetchall()

            if not rows:
                return "No results found."

            # Format as table
            # Convert all values to strings and get maximum width for each column
            str_rows = []
            col_widths = [len(str(col)) for col in columns]

            for row in rows:
                str_row = [str(val) if val is not None else "NULL" for val in row]
                str_rows.append(str_row)
                # Update column widths if necessary
                for i, val in enumerate(str_row):
                    if i < len(col_widths):
                        col_widths[i] = max(col_widths[i], len(val))

            # Build the table
            result = []

            result.append(formatted_sql)
            result.append("\n")

            # Header
            header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
            result.append(header)

            # Separator
            separator = "-+-".join("-" * width for width in col_widths)
            result.append(separator)

            # Data rows
            for row in str_rows:
                result.append(" | ".join(val.ljust(col_widths[i]) for i, val in enumerate(row)))

            return "\n".join(result)
        except Exception as e:
            logger.info(f"Failed to execute query: {str(e)}")
            raise Exception(f"Failed to execute query: {str(e)}")
        finally:
            cursor.close()
    except Exception as e:
        logger.info(f"Failed to connect to Snowflake: {str(e)}")
        raise Exception(f"Failed to connect to Snowflake: {str(e)}")


def main():
    """Entry point for the MCP server."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("\n👋 MCP Snowflake Reader stopped by user.")


if __name__ == "__main__":
    main()


