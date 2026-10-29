import oracledb

DB_USER = "COMPLAINT_APP"
DB_PASSWORD = "CloudComplaint@"
DB_DSN = "localhost:1521/XEPDB1"


def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )
    
