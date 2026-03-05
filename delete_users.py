import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("DELETE FROM logs")

conn.commit()
conn.close()

print("All logs deleted")