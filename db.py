# import sqlite3
# con = sqlite3.connect('example.db')
#
# cur = con.cursor()

# # Create table
# cur.execute('''CREATE TABLE users
#                (id int, name text)''')
#
# # Insert a row of data
# cur.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
#
# # Save (commit) the changes
# con.commit()
#
# # We can also close the connection if we are done with it.
# # Just be sure any changes have been committed or they will be lost.
# con.close()