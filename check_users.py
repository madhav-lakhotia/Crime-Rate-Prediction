import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# ✅ Users ka data fetch karna
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
conn.close()

if users:
    print("\n📌 Registered Users:")
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Password: {user[2]}")
else:
    print("❌ No users found in database!")
