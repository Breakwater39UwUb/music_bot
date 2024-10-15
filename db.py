'''Module for db connection and usage'''

from dbutils.pooled_db import PooledDB
import csv
import json
import uuid
from datetime import datetime
import pymysql
from pymysql.constants.ER import DUP_ENTRY
import pymysql.err as sqlError
from pymysql.err import(
    OperationalError,
    IntegrityError,
    ProgrammingError,
    DataError,
    InternalError,
    NotSupportedError)
import utils
from dc_path import DB_CONFIG

DEFAULT_HOST = 'localhost'
DEFAULT_DB = 'dc_bot'
DEFAULT_TABLE = 'songs'

TABLES = {
    'artists': 'artists',
    'company': 'record_company',
    'songs': 'songs',
    'song_tags': 'tags',
    'tag_labels': 'tag_labels',
    'users': 'users'
}

log = utils.Debug_Logger('database')

try:
    db_pool = PooledDB(
        pymysql,
        maxconnections=10,
        mincached=2,
        maxcached=5,
        blocking=True,
        ping=4,
        host=DB_CONFIG['remotehost'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['db_name']
    )
    log.log(f"Connected to {DB_CONFIG['user']}@{DB_CONFIG['remotehost']}:{DB_CONFIG['port']}", 20)
except pymysql.MySQLError as e:
    db_pool = PooledDB(
        pymysql,
        maxconnections=10,
        mincached=2,
        maxcached=5,
        blocking=True,
        ping=4,
        host=DB_CONFIG['localhost'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['db_name']
    )
    log.log(f"Connected to {DB_CONFIG['user']}@{DB_CONFIG['localhost']}:{DB_CONFIG['port']}", 20)

def insert_to_table(data: tuple,
                    table: str = 'artists',
                    db=None):
    """
    Inserts a new record into the specified table in the database.

    This function connects to the database using the provided connection object (db). If no connection object is provided,
    it attempts to initialize a new connection using the default database settings. The function then checks if the specified
    table exists in the database. If the table does not exist, it raises a ValueError.

    After ensuring the table exists, the function constructs an INSERT command based on the table name and the provided data.
    It executes the command using the cursor and commits the changes to the database. Finally, it closes the database connection.

    Parameters:
    data (tuple): A tuple containing the values to be inserted into the table.
    table (str): The name of the table in the database. Default is 'artists'.
    db (pymysql.connections.Connection): The database connection object. If not provided, a new connection will be initialized.

    Returns:
    None
    """
    if db is None:
        db = init_db()
        if db is None:
            return 'failed'

    if not check_exist_table(table, db):
        raise ValueError('Must given table name exist in database.')

    commands = {
        TABLES['artists']: f"INSERT INTO `{table}` (`ArtistName`, `ArtistName_Alt`, `Company`) VALUES(%s, %s, %s)",
        TABLES['company']: f"INSERT INTO `{table}` (`ID`, `Name`) VALUES(%s, %s)",
        TABLES['songs']: f"INSERT INTO `{table}` (`ID`, `Title`, `Artist`, `Recommender`) VALUES(%s, %s, %s, %s)",
        TABLES['song_tags']: f"INSERT INTO `{table}` (`SongID`, `Tag`) VALUES(%s, %s)",
        TABLES['tag_labels']: f"INSERT INTO `{table}` (`ID`, `TagType`, `TagName`) VALUES(%s, %s, %s)",
        TABLES['users']: f"INSERT INTO `{table}` (`UserID`, `Name`) VALUES(%s, %s)"
    }

    cursor = db.cursor()
    try:
        cursor.execute(commands[table], data)
        db.commit()
    except pymysql.IntegrityError as e:
        if e.args[0] == 1452:
            print("IntegrityError: 1452 - Foreign key constraint failed.")
        else:
            print(f"Unexpected IntegrityError: {e.args[0]}")
    finally:
        db.close()



def check_exist_table(table_name: str, db=None):
    '''Check if the table is exist in database
    
    Parameters:
    table_name: table name in innoserve database

    Returns:
    result: True if the table exists in database
    '''

    if db is None:
        # No db object passed, initial one
        db = init_db()

        if db is None:
            return
        cursor = db.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        db.close()
    else:
        # Use given db object
        cursor = db.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()

    if result is None:
        return False
    return True
