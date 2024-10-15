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
    Inserts a record into the specified table in the database. If no database connection is provided, 
    a new connection is obtained from the connection pool.

    :param data: The data to be inserted, structured as a tuple. The format should match the columns expected 
                 by the specified table. For example, for the 'artists' table, it should be (ArtistName, ArtistName_Alt, Company).
    :type data: tuple
    :param table: The name of the table to insert data into. Must correspond to an entry in the TABLES dictionary, 
                  which maps table names to their respective INSERT commands.
    :type table: str
    :param db: A database connection object. If None, a new connection is created from the database pool.
               Defaults to None.
    :type db: Optional[Connection]
    
    :raises OperationalError: If an error related to the database's operation occurs.
    :raises IntegrityError: If the insert violates a constraint, such as a unique or foreign key constraint.
    :raises ProgrammingError: If there's an error in the SQL syntax.
    :raises DataError: If the data provided is out of range or otherwise incorrect.
    :raises InternalError: If the database encounters an internal error.
    :raises NotSupportedError: If the attempted operation is not supported by the database.
    :raises pymysql.MySQLError: For any other MySQL-specific errors.
    :raises Exception: For any other unexpected errors.
    
    :note: The function commits the transaction if the insert is successful. In case of an error, 
           it rolls back the transaction.
    :note: If `table` is 'song_tags', the function will insert multiple rows for each tag in the second element 
           of the data tuple.
    """
    if db is None:
        db = db_pool.connection()
        close_db = True
    close_db = False

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
