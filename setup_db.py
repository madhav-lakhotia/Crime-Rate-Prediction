import sqlite3

conn = sqlite3.connect("users.db")  # Ye database file open karega
cursor = conn.cursor()

# Check table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())  # Ye database ki tables dikhayega

conn.close()
