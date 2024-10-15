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
DEFAULT_DB_USER = 'dc_bot'

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

def fetch_tags(type: str, table: str = TABLES['tag_labels']):
    tags = []
    db = db_pool.connection()
    cursor = db.cursor()
    cursor.execute(f"SELECT TagName FROM `{table}` WHERE TagType = %s", (type,))
    db.commit()

    results = cursor.fetchall()
    for row in results:
        tags.append(row[0])
    cursor.close()
    db.close()

    return tags

def insert_to_table(data: tuple,
                    table: str,
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
        db = db_pool.connection()
        close_db = True
    close_db = False
    # db.ping(True)

    # if not check_exist_table(table, db):
    #     raise ValueError('Must given table name exist in database.')

    commands = {
        TABLES['artists']: f"INSERT INTO `{table}` (`ArtistName`, `ArtistName_Alt`, `Company`) VALUES(%s, %s, %s)",
        TABLES['company']: f"INSERT INTO `{table}` (`ID`, `Name`) VALUES(%s, %s)",
        TABLES['songs']: f"INSERT INTO `{table}` (`ID`, `Title`, `Artist`, `Recommender`) VALUES(%s, %s, %s, %s)",
        TABLES['song_tags']: f"INSERT INTO `{table}` (`SongID`, `Tag`) VALUES(%s, %s)",
        TABLES['tag_labels']: f"INSERT INTO `{table}` (`ID`, `TagType`, `TagName`) VALUES(%s, %s, %s)",
        TABLES['users']: f"INSERT INTO `{table}` (`UserID`, `Name`) VALUES(%s, %s)"
    }

    try:
        cursor = db.cursor()
        if table == TABLES['song_tags']:
            for tag in data[1]:
                cursor.execute(commands[table], (data[0], tag))
        else:
            cursor.execute(commands[table], data)
        db.commit()
    except OperationalError as e:
        db.rollback()
        raise OperationalError(f'{e}')
    except IntegrityError as e:
        db.rollback()
        raise IntegrityError(f'{e}')
    except ProgrammingError as e:
        db.rollback()
        raise ProgrammingError(f'{e}')
    except DataError as e:
        db.rollback()
        raise DataError(f'{e[1]}')
    except InternalError as e:
        db.rollback()
        raise InternalError(f'{e}')
    except NotSupportedError as e:
        db.rollback()
        raise NotSupportedError(f'{e}')
    except pymysql.MySQLError as e:
        db.rollback()
        raise pymysql.MySQLError(f"MySQL error occurred: {e}")
    except Exception as unexpected:
        db.rollback()
        raise unexpected
    finally:
        cursor.close()
        if close_db:
            db.close()

def find_artists(name: str|int,
                 table: str = TABLES['artists'],
                 db = None):
    '''
    May return string that contains \\u3000
    '''
    if db is None:
        db = db_pool.connection()
        close_db = True
    close_db = False
    artists_names = []

    # if not check_exist_table(table, db):
    #     raise ValueError('Must given table name exist in database.')

    try:
        cursor = db.cursor()
        if type(name) == int:
            query = f"SELECT ArtistID, ArtistName FROM `{table}`\
                WHERE ArtistID = %s"
            cursor.execute(query, (name,))
        elif type(name) == str:
            query = f"SELECT ArtistID, ArtistName FROM `{table}`\
            WHERE ArtistName LIKE %s\
            OR ArtistName_Alt LIKE %s\
            LIMIT 25"
            cursor.execute(query, ('%' + name + '%', '%' + name + '%'))
    except OperationalError as e:
        raise OperationalError(f'{e}')
    except IntegrityError as e:
        raise IntegrityError(f'{e}')
    except ProgrammingError as e:
        raise ProgrammingError(f'{e}')
    except DataError as e:
        raise DataError(f'{e[1]}')
    except InternalError as e:
        raise InternalError(f'{e}')
    except NotSupportedError as e:
        raise NotSupportedError(f'{e}')
    except pymysql.MySQLError as e:
        raise pymysql.MySQLError(f"MySQL error occurred: {e}")
    except Exception as unexpected:
        raise unexpected
    finally:
        cursor.close()
        if close_db:
            db.close()

    # Fetch and print the results
    results = cursor.fetchall()
    for row in results:
        artists_names.append(row)

    return artists_names

def submit_song(title: str,
                artist_id: int,
                recommender: tuple,
                table: str = TABLES['songs']):
    '''Submit a new song

    :param tuple recommender: (user_id, user_name)
    :return (tuple) data: (ID, title, artist name, user ID)
    '''

    # db = init_db(user=DEFAULT_DB_USER, host='localhost')
    db = db_pool.connection()
    if check_exist_row(recommender[0], db) == False:
        insert_to_table(recommender, TABLES['users'], db)
    data = [uuid.uuid4(), title, int(artist_id), recommender[0]]
    insert_to_table(tuple(data), table, db)
    data[2] = find_artists(name=data[2], db=db)[0][1]
    db.close()

    return (data)

def add_song_tags(song_id: uuid.UUID,
                  tags: list,
                  table: str = TABLES['song_tags']):
    '''Add tags to a song'''

    db = db_pool.connection()
    data = (song_id,) + tuple(tags)
    insert_to_table(data, table, db)
    db.close()

def check_exist_row(data: str,
                    column: str,
                    table: str,
                    db = None):
    '''Check if user exists'''

    if table not in TABLES:
        raise ValueError('Must given table name exist in database.')

    query = f'SELECT * FROM `{table}` WHERE {column} = %s'

    if db is None:
        db = db_pool.connection()
        close_db = True
    close_db = False

    try:
        cursor = db.cursor()
        cursor.execute(query, (data,))
        result = cursor.fetchone()
    except OperationalError as e:
        raise OperationalError(f'{e}')
    except IntegrityError as e:
        raise IntegrityError(f'{e}')
    except ProgrammingError as e:
        raise ProgrammingError(f'{e}')
    except DataError as e:
        raise DataError(f'{e[1]}')
    except InternalError as e:
        raise InternalError(f'{e}')
    except NotSupportedError as e:
        raise NotSupportedError(f'{e}')
    except pymysql.MySQLError as e:
        raise pymysql.MySQLError(f"MySQL error occurred: {e}")
    except Exception as unexpected:
        raise unexpected
    finally:
        cursor.close()
        if close_db:
            db.close()

    if result is None:
        return False
    return True

# def init_db(user: str = 'root',
#             db_name: str = DEFAULT_DB_USER,
#             host: str = 'localhost') -> pymysql.connections.Connection:
#     """
#     Initialize a connection to a MySQL database.

#     This function attempts to establish a connection to a MySQL database using the provided user, database name, and host.
#     If the connection fails, it logs an error message and returns None.

#     :param user (str): The username for the MySQL database. Default is 'root'.
#     :param db_name (str): The name of the MySQL database. Default is 'dc_bot'.
#     :param host (str): The host of the MySQL database. Default is 'localhost'.

#     Returns:
#     pymysql.connections.Connection: A connection object to the MySQL database if successful, otherwise None.
#     """
#     log = utils.Debug_Logger(__name__)
#     forward_ip, forward_port, pwd = get_connection_args(host)

#     try:
#         return pymysql.connect(host=forward_ip,
#                                port=forward_port,
#                                user=user,
#                                database=db_name,
#                                password=pwd,
#                                charset='utf8mb4')
#     except OperationalError as err:
#         forward_ip, forward_port, pwd = get_connection_args('localhost')
#         log.log(f'Error connecting to MySQL database, check your database host and port.\nhost: {forward_ip}\nport: {forward_port}', 40)
#         log.log(f'Trying to connect localhost: {forward_ip}\nport: {forward_port}', 40)
#         try:
#             return pymysql.connect(host=forward_ip,
#                         port=forward_port,
#                         user=user,
#                         database=db_name,
#                         password=pwd,
#                         charset='utf8mb4')
#         except OperationalError as err:
#             log.log(f'Error connecting to MySQL database, check your database host and port.\nhost: {forward_ip}\nport: {forward_port}', 40)
#             raise err
#     except Exception as err:
#         raise err
