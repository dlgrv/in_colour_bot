from mysql.connector import MySQLConnection, Error
from dbconfig import read_db_config

table_name = 'incolourbot'

#переписать весь код на dictionary=True

# CHECK - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_user(uid):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    query = f'SELECT *  ' \
            f'FROM {table_name} ' \
            f'WHERE uid = "{uid}" ' \
            f'LIMIT 1'
    try:
        cursor.execute(query)
        rows = cursor.fetchone()
        print(f'[DataBase] --> {rows} (check_user)')
        return rows
    except Error as e:
        print(f'[DataBase] ERR: {e} (check_user)')
        pass
    finally:
        cursor.close()
        conn.close()

# ADD - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def add_user(uid, username):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    query = f"INSERT INTO {table_name} (uid, username) " \
            f"VALUES ('{uid}', '{username}')"
    try:
        cursor.execute(query)
        conn.commit()
        print(f'[DataBase] --> (add_user)')
    except Error as e:
        print(f'[DataBase] ERR: {e} (add_user)')
        pass
    finally:
        cursor.close()
        conn.close()