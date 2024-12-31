import asyncio
import os
from dap.api import DAPClient
from dap.dap_types import Credentials, Format, SnapshotQuery
from dotenv import load_dotenv
from utils.constants import NAMESPACE, TABLE_SCHEMAS_PATH, TABLES_FOR_KPIS_IN_CANVAS

# Load environment variables from .env file
def load_env_vars() -> tuple[str, str, str]:
    """
    Loads environment variables (DAP_API_URL, DAP_CLIENT_ID, DAP_CLIENT_SECRET)
    from a .env file.

    Returns:
        A tuple containing the base URL, client ID, and client secret.
    """
    load_dotenv()
    base_url = os.environ["DAP_API_URL"]
    client_id = os.environ["DAP_CLIENT_ID"]
    client_secret = os.environ["DAP_CLIENT_SECRET"]
    return base_url, client_id, client_secret

# Create credentials
def create_credentials() -> Credentials:
    """
    Creates a Credentials object using the loaded client ID and secret.

    Returns:
        A Credentials object for DAPClient authentication.
    """
    _, client_id, client_secret = load_env_vars()
    return Credentials.create(client_id=client_id, client_secret=client_secret)

# Get table schema
async def get_table_schema(namespace: str, table: str, credentials:Credentials = None):
    """
    Fetches the schema for a given table in the specified namespace.

    Args:
        namespace (str): The namespace of the table.
        table (str): The name of the table.
        credentials (Credentials, optional): Optional credentials object. Defaults to None.

    Returns:
        dict: The schema dictionary for the requested table.
    """
    if credentials is None:
        credentials = create_credentials()
    async with DAPClient() as session:
        schema = await session.get_table_schema(namespace, table)
        return schema
    
async def get_tables(namespace: str, credentials:Credentials = None):
    """
    Retrieves a list of all tables within the specified namespace.

    Args:
        namespace (str): The namespace to list tables from.
        credentials (Credentials, optional): Optional credentials object. Defaults to None.

    Returns:
        List[str]: A list of table names in the specified namespace.
    """
    if credentials is None:
        credentials = create_credentials()
    async with DAPClient() as session:
        tables = await session.get_tables(namespace)
        return tables

# Download all table schemas
async def download_all_table_schemas(namespace: str, output_directory: str = TABLE_SCHEMAS_PATH, credentials:Credentials = None):
    """
    Downloads schemas for all tables within a namespace to the specified output directory.

    Args:
        namespace (str): The namespace containing the tables.
        output_directory (str): The directory to save downloaded schemas. The default one is in folder "table_schemas"
        credentials (Credentials, optional): Optional credentials object. Defaults to None.
    """
    if credentials is None: 
        credentials = create_credentials()
    async with DAPClient() as session:
        tables = await session.get_tables(namespace)
        for table in tables:
            await session.download_table_schema(namespace=namespace, table=table, output_directory=output_directory)
            print(f"Downloaded schema for '{table}'")

# Download table data
async def download_table_data(namespace: str, table: str, output_directory: str, credentials: Credentials = None):
    """
    Downloads data for a specific table in the specified format and saves it to the output directory.

    Args:
        namespace (str): The namespace of the table.
        table (str): The name of the table to download data from.
        output_directory (str): The directory to save downloaded data.
        credentials (Credentials, optional): Optional credentials object. Defaults to None.
    """
    if credentials is None:
        credentials = create_credentials()
    
    file_name = f"{table}_data.csv"
    output_file_dir = os.path.join(output_directory, file_name)
    async with DAPClient() as session:
        query = SnapshotQuery(format=Format.JSONL, mode=None)
        await session.download_table_data(
            namespace=namespace, table=table, query=query, output_directory=output_file_dir, decompress=True
        )

# Download data for given tables 
async def download_tables_data(namespace: str, tables: list, output_directory: str, credentials: Credentials = None):
    """
    Downloads data for a list of tables in the specified namespace to the output directory.

    Args:
        namespace (str): The namespace of the tables.
        tables (List[str]): A list of table names to download data for.
        output_directory (str): The directory to save downloaded data.
        credentials (Credentials, optional): Optional credentials object. Defaults to None.
    """
    if credentials is None:
        credentials = create_credentials()
    if tables is None:
        tables = get_tables(namespace)
    async with DAPClient() as session:
        query = SnapshotQuery(format=Format.JSONL, mode=None)
        for table in tables:
            await session.download_table_data(
                namespace=namespace, table=table, query=query, output_directory=output_directory, decompress=True
            )

# Example usage:
if __name__ == "__main__":
    # Run independently
    # asyncio.run(get_table_schema(namespace=NAMESPACE, table="accounts"))
    # asyncio.run(download_all_table_schemas(namespace=NAMESPACE))
    # asyncio.run(get_tables(namespace=NAMESPACE))
    # asyncio.run(download_table_data(namespace=NAMESPACE, table="access_tokens", output_directory=CSV_FOLDER_PATH))
    asyncio.run(download_tables_data(namespace=NAMESPACE, tables=TABLES_FOR_KPIS_IN_CANVAS, output_directory=os.getcwd()))