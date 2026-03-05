import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cur = conn.cursor()

name = "Name"
password = generate_password_hash("Name1234")

cur.execute(
"INSERT INTO users (name, password) VALUES (?, ?)",
(name, password)
)

conn.commit()
conn.close()

print("User added successfully")