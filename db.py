'''Module for db connection and usage'''
# TODO: Remove all db objects and state flow in functions after code review

import pymysql
from pymysql.constants.ER import DUP_ENTRY
import csv
import json
import utils
import uuid

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

def fetch_all(table: str):
    '''Download all reviews from given table'''

    db = init_db(user='dc_bot', host='remote')
    if db is None:
        return
    cursor = db.cursor()
    command = f"SELECT * FROM `{table}`"
    cursor.execute(command)
    reviews = cursor.fetchall()
    db.close()

    path = table + '.json'
    
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(reviews, file, ensure_ascii=False, indent=4)
    print(f'Table saved to: {path}')
    return reviews

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
        db = init_db(user='dc_bot', host='remote')
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

def find_artists(name: str,
                 table: str = TABLES['artists'],
                 db = None):
    '''
    May return string that contains \\u3000
    '''
    if db is None:
        db = init_db(user='dc_bot', host='remote')
    if db is None:
        return 'failed'

    if not check_exist_table(table, db):
        raise ValueError('Must given table name exist in database.')

    cursor = db.cursor()
    artists_names = []

    query = f"SELECT ArtistName FROM `{table}`\
        WHERE ArtistName LIKE %s\
        OR ArtistName_Alt LIKE %s\
        LIMIT 25"
    cursor.execute(query, ('%' + name + '%', '%' + name + '%'))

    # Fetch and print the results
    results = cursor.fetchall()
    for row in results:
        artists_names.append(row[0])
    return artists_names

def check_exist_table(table_name: str, db=None):
    '''Check if the table is exist in database
    
    Parameters:
    table_name: table name in innoserve database

    Returns:
    result: True if the table exists in database
    '''

    if db is None:
        # No db object passed, initial one
        db = init_db(user='dc_bot', host='remote')

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

def get_connection_args(remote: str='localhost') -> tuple:
    """
    Retrieve the connection arguments for a MySQL database based on the specified remote host.

    This function returns a tuple containing the host IP, port number, and password for connecting to the MySQL database.
    The function supports two remote hosts: 'localhost' and 'lab404'. If no remote host is specified, the default is 'localhost'.

    :param remote (str): The remote host for the MySQL database. It can be either 'localhost' or 'lab404'. Default is 'localhost'.

    Returns:
    tuple: A tuple containing the host IP, port number, and password for connecting to the MySQL database.
    """
    if remote == 'localhost':
        return 'localhost', 3306, 'root'
    if remote == 'remote':
        return '1.170.130.56', 3306, '2wsx!QAZ'


def init_db(user: str = 'root',
            db_name: str = 'dc_bot',
            host: str = 'localhost') -> pymysql.connections.Connection:
    """
    Initialize a connection to a MySQL database.

    This function attempts to establish a connection to a MySQL database using the provided user, database name, and host.
    If the connection fails, it logs an error message and returns None.

    :param user (str): The username for the MySQL database. Default is 'root'.
    :param db_name (str): The name of the MySQL database. Default is 'dc_bot'.
    :param host (str): The host of the MySQL database. Default is 'localhost'.

    Returns:
    pymysql.connections.Connection: A connection object to the MySQL database if successful, otherwise None.
    """
    log = utils.Debug_Logger('init_db')

    forward_ip, forward_port, pwd = get_connection_args(host)

    try:
        return pymysql.connect(host=forward_ip,
                               port=forward_port,
                               user=user,
                               database=db_name,
                               password=pwd,
                               charset='utf8mb4')
    except pymysql.err.OperationalError as err:
        log.log(f'Error connecting to MySQL database, check your database host and port.\nhost: {forward_ip}\nport: {forward_port}', 30)
        return None

