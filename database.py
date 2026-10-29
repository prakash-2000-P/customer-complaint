import streamlit as st
import psycopg2


def get_connection():
    db = st.secrets["postgres"]
    return psycopg2.connect(
        host=db["host"],
        port=int(db.get("port", 5432)),
        dbname=db.get("dbname", "postgres"),
        user=db["user"],
        password=db["password"],
        sslmode="require",
        connect_timeout=10,
    )
