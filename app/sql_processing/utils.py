import psycopg
from psycopg.rows import dict_row

def connect_sql_db(DB_PARAMS: dict):
    conn = psycopg.connect(**DB_PARAMS)
    return conn

def fetch_conversations(DB_PARAMS: dict, table_name: str = 'conversations'):
    conn = connect_sql_db(DB_PARAMS)
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(f'SELECT * FROM {table_name}')
            conversations = cursor.fetchall()
        return conversations
    finally:
        conn.close()

def store_conversations(DB_PARAMS: dict, prompt, response, table_name: str = 'conversations'):
    conn = connect_sql_db(DB_PARAMS)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO {table_name} (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)',
                (prompt, response)
            )
            conn.commit()
    finally:
        conn.close()

def remove_last_conversation(DB_PARAMS: dict, table_name: str = 'conversations'):
    conn = connect_sql_db(DB_PARAMS)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'DELETE FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})')
            conn.commit()
    finally:
        conn.close()