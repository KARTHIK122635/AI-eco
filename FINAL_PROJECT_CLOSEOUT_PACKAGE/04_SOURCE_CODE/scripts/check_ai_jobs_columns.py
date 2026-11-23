import sqlite3

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(ai_jobs);")
cols = cursor.fetchall()
print("Columns in ai_jobs:")
for col in cols:
    print(col)
conn.close()
