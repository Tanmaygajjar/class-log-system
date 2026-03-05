import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cur = conn.cursor()

name = "Name"
new_password = generate_password_hash("NEWPASSWORD")

cur.execute(
"UPDATE users SET password=? WHERE name=?",
(new_password, name)
)

conn.commit()
conn.close()

print("Password updated successfully")