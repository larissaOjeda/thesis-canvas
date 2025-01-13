from utils.constants import NAMESPACE, TABLES_FOR_KPIS_IN_CANVAS
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

db_connection = DatabaseConnection(DATABASE_URL)

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

async def main():
    if not isinstance(TABLES_FOR_KPIS_IN_CANVAS, list) or not TABLES_FOR_KPIS_IN_CANVAS:
        raise ValueError("TABLES_FOR_KPIS must be a non-empty list.")

    for table in TABLES_FOR_KPIS_IN_CANVAS:
        await synchronize_data_in_db(table)


if __name__ == "__main__":
    if not isinstance(TABLES_FOR_KPIS_IN_CANVAS, list) or not TABLES_FOR_KPIS_IN_CANVAS:
        raise ValueError("TABLES_FOR_KPIS must be a non-empty list.")

    
    asyncio.run(run_tasks_sequentially(tables=TABLES_FOR_KPIS_IN_CANVAS))

    # asyncio.run(main())
