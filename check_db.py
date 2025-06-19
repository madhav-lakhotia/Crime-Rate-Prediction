import sqlite3

conn = sqlite3.connect("users.db")  # Database open karega
cursor = conn.cursor()

# ✅ Table check karne ka command
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
table = cursor.fetchone()

if table:
    print("✅ 'users' table exists!")
else:
    print("❌ 'users' table NOT found!")

conn.close()
