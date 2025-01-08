from utils.constants import NAMESPACE, TABLES_FOR_KPIS_IN_CANVAS, TABLES_FOR_KPIS_IN_CANVAS_LOGS
from dap.api import DAPClient
from dap.integration.database import DatabaseConnection
from dap.replicator.sql import SQLReplicator
from dotenv import load_dotenv
import os
import asyncio
from typing import List

load_dotenv() 
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

connection_string: str = DATABASE_URL
db_connection = DatabaseConnection(connection_string)


async def initialize_table_in_db(table_name: str, namespace: str = NAMESPACE): 
    async with DAPClient() as session:
        await SQLReplicator(session, db_connection).initialize(namespace, table_name)


async def synchronize_data_in_db(table_name: str, namespace: str = NAMESPACE): 
    async with DAPClient() as session:
        await SQLReplicator(session, db_connection).synchronize(namespace, table_name)


async def run_tasks_sequentially(tables: List[str], namespace: str = NAMESPACE):
    for table_name in tables:
        try:
            print(f"Processing table: {table_name}")
            await initialize_table_in_db(table_name=table_name, namespace=namespace)
            await synchronize_data_in_db(table_name=table_name, namespace=namespace)
            print(f"Successfully processed table: {table_name}")
        except Exception as e:
            print(f"Error processing table {table_name}: {e}")


async def check_table_metadata(namespace: str, table_name: str):
    async with DAPClient() as session:
        try:
            schema = await session.get_table_schema(namespace, table_name)
            print(f"Schema for {table_name} in {namespace}: {schema}")
        except Exception as e:
            print(f"Error retrieving schema for {table_name} in {namespace}: {e}")


async def test_web_logs_sync():
    async with DAPClient() as session:
        try:
            await SQLReplicator(session, db_connection).initialize("canvas_logs", "web_logs")
            await SQLReplicator(session, db_connection).synchronize("canvas_logs", "web_logs")
            print("Successfully initialized and synchronized web_logs in canvas_logs namespace.")
        except Exception as e:
            print(f"Error with web_logs synchronization: {e}")



async def main():
    if not isinstance(TABLES_FOR_KPIS_IN_CANVAS, list) or not TABLES_FOR_KPIS_IN_CANVAS:
        raise ValueError("TABLES_FOR_KPIS must be a non-empty list.")

    for table in TABLES_FOR_KPIS_IN_CANVAS:
        await synchronize_data_in_db(table)



if __name__ == "__main__":
    # if not isinstance(TABLES_FOR_KPIS_IN_CANVAS, list) or not TABLES_FOR_KPIS_IN_CANVAS:
    #     raise ValueError("TABLES_FOR_KPIS must be a non-empty list.")

    # asyncio.run(test_web_logs_sync())
    
    # asyncio.run(run_tasks_sequentially(tables=TABLES_FOR_KPIS_IN_CANVAS))
    # asyncio.run(run_tasks_sequentially(tables=TABLES_FOR_KPIS_IN_CANVAS_LOGS, namespace="canvas_logs"))

    asyncio.run(main())
