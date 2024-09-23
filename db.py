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

def db_upload_file(filename: str,
                   host_name: str = 'localhost',
                   db_name: str = DEFAULT_DB,
                   table_name: str = 'rumors',
                   file_format: str = 'json'):
    """Upload in given file

    Args:
        filename: File under ./SaveData/
        db_name: Database to connect, default connect to innoserve database
        file_format: Default = 'json'
    No returns
    """

    if file_format not in ['csv', 'json']:
        raise Exception('file_format must be csv or json')
    
    db = init_db(db_name, host_name)
    log = utils.Debug_Logger('init_db')

    if db is None:
        log.log('Failed to connect to MySQL database.', 30)
        return

    cursor = db.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    # cursor.execute(command)

    with open(filename, 'r', encoding='utf-8') as file:
        if file_format == 'csv':
            lines = csv.reader(file)
        if file_format == 'json':
            lines = json.load(file)

        for line in lines:
            # Update table
            command = f"INSERT INTO {table_name}\
                (id, publish_date, title, tag, content) VALUES\
                (%s, %s, %s, %s, %s)"

            if file_format == 'csv':
                id, publish_date, title, tag, content = line[0], line[1], line[2], line[3], line[4]
            if file_format == 'json':
                id = int(line['id'])
                publish_date = line['date']
                title = line['title']
                tag = line['tag']
                content = line['content']

            article = (id, publish_date, title, tag, content)

            try:
                cursor.execute(command, article)
                db.commit()
            except pymysql.IntegrityError as e:
                if e.args[0] == DUP_ENTRY:
                    log.log(e)
                    pass
        db.close()
        log.log(f'{filename} uploaded successfully.')

def fetch_all(table: str):
    '''Download all reviews from given table'''

    db = init_db()
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
    if remote == 'lab404':
        return '192.168.196.201', 3306, 'lab404'


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

