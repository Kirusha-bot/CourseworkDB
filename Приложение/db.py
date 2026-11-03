import mysql.connector
import pandas as pd
from datetime import datetime
import streamlit as st

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Meliod@s200620111987710',
    'database': 'Военный_округ',
    'charset': 'utf8mb4'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

@st.cache_data(ttl=60)
def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def run_execute(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

def init_history_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Action_History (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            action_time     DATETIME NOT NULL,
            action_type     VARCHAR(20) NOT NULL,
            table_name      VARCHAR(50) NOT NULL,
            record_id       INT,
            details         TEXT,
            undo_query      TEXT,
            performed_by    VARCHAR(50)
        )
    """)
    conn.commit()
    conn.close()

def log_action(action_type, table_name, record_id, details, undo_query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Action_History (action_time, action_type, table_name, record_id, details, undo_query, performed_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (datetime.now(), action_type, table_name, record_id, details, undo_query,
          st.session_state.get("username", "admin")))
    conn.commit()
    conn.close()
    st.cache_data.clear()
