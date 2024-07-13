import psycopg
from psycopg.rows import dict_row

def connect_sql_db(DB_PARAMS: dict):
    """
    建立連接PostgresSQL資料庫的連線
    """
    conn = psycopg.connect(**DB_PARAMS)
    return conn

def fetch_conversations(DB_PARAMS: dict, table_name: str = 'conversations'):
    """從PostgreSQL資料庫中取出所有對話紀錄

    Returns:
        list[dict]: 對話紀錄 (list[{'id': int, 'prompt': str, 'response': str}])
    """
    conn = connect_sql_db(DB_PARAMS)
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(f'SELECT * FROM {table_name}')
            conversations = cursor.fetchall()
        return conversations
    finally:
        conn.close()

def store_conversations(DB_PARAMS: dict, prompt, response, table_name: str = 'conversations'):
    """將一輪的對話紀錄儲存進PostgreSQL資料庫

    Args:
        prompt (str): 使用者輸入的提示詞
        response (str): LLM的回答
    """
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
    """從資料庫中移除最後一筆對話紀錄
    """
    conn = connect_sql_db(DB_PARAMS)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'DELETE FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})')
            conn.commit()
    finally:
        conn.close()