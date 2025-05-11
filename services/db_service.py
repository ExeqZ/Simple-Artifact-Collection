import pyodbc
import os
import struct
from azure.identity import DefaultAzureCredential

def init_db(app):
    app.config['SQL_SERVER'] = os.environ.get("SQL_SERVER")
    app.config['SQL_DATABASE'] = os.environ.get("SQL_DATABASE")

def get_db_connection():
    credential = DefaultAzureCredential()
    access_token = credential.get_token("https://database.windows.net/").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(access_token)}s', len(access_token), access_token)
    SQL_COPT_SS_ACCESS_TOKEN = 1256

    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.environ.get('SQL_SERVER')};"
        f"DATABASE={os.environ.get('SQL_DATABASE')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    return pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})