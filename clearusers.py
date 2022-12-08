# clear the users in the database
from sqlite3 import connect
import sqlite3

conn = sqlite3.connect('MajorMonkey.db')
c = conn.cursor()
c.execute("DELETE FROM Users;")
conn.commit()
conn.close()