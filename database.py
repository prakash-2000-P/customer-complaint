
import streamlit as st
import psycopg2

def get_connection():
    db = st.secrets["postgres"]
    return psycopg2.connect(
        host=db["host"],
        port=int(db["port"]),
        dbname=db["dbname"],
        user=db["user"],
        password=db["password"],
        sslmode="require",
        connect_timeout=10,
    )
