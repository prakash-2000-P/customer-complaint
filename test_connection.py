from database import get_connection

try:
    connection = get_connection()
    print("Oracle connection successful!")

    cursor = connection.cursor()
    cursor.execute("SELECT USER FROM DUAL")
    print("Connected user:", cursor.fetchone()[0])

    cursor.close()
    connection.close()

except Exception as e:
    print("Connection failed:", e)