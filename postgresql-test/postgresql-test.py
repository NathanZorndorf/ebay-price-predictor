import psycopg2

dbname='test-db1'
user='nathan'
host='localhost'

try:
    conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
    print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

cur.execute()

rows = cur.fetchall()

if rows:
	for row in rows:
    	print row[0]


