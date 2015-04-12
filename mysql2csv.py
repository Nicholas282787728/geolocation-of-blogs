import MySQLdb as mdb
import sys
import csv
import json

con = mdb.connect('localhost', 'root', '', 'myblogs');
cur = con.cursor()

query = "SELECT * FROM state_profile_post_content"
cur.execute(query)
rows = cur.fetchall()

print "number of rows fetched:", len(rows)

csv_outFile = open('myblogs.csv', "w")
csv_writer = csv.writer(csv_outFile)

for row in rows:
	csv_writer.writerow( row )
	
csv_outFile.close()


# with open('myblogs.csv', 'rb') as csvfile:
#     csvreader = csv.reader(csvfile, delimiter=',')
#     for row in csvreader:
#         print ' || '.join(row)