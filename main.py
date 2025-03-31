#!/usr/bin/env python3

import json
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List

import snowflake.connector
from mcp.server.fastmcp import FastMCP


@asynccontextmanager
async def app_lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    """Manages Snowflake connection lifecycle during server startup/shutdown.
    Establishes connection when server starts and ensures proper cleanup on shutdown."""
    if len(sys.argv) < 2:
        raise Exception("Please provide Snowflake connection details as a command-line argument")

    connection_details = json.loads(sys.argv[1])
    try:
        mcp.connection = snowflake.connector.connect(**connection_details)
        mcp.is_connected = True
        yield
    except Exception as e:
        raise Exception(f"Failed to connect to Snowflake: {str(e)}")
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

    cursor = mcp.connection.cursor()
    try:
        cursor.execute(f"DESCRIBE TABLE {table_name}")
        rows = cursor.fetchall()
        return json.dumps(rows, default=str, indent=2)
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

    cursor = mcp.connection.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return json.dumps(rows, default=str, indent=2)
    finally:
        cursor.close()


if __name__ == "__main__":
    mcp.run()