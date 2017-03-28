import psycopg2
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import requests


start_index = input('Which index are you starting at?')

dbname='ebay'
user='nathan'
host='localhost'
TABLE_NAME = 'completed_items'

try:
    conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
    print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
except:
    print "ERROR: Unable to connect to the database." 
    sys.exit("Check database connection settings and try again.")

cur = conn.cursor()

SQL = '''
SELECT ci."itemId", ci."viewItemURL" 
FROM completed_items as ci;
'''
cur.execute(SQL)
data = [(int(itemId),str(url)) for itemId,url in cur.fetchall()]


SQL = '''
SELECT count(*) 
FROM completed_items;
'''
cur.execute(SQL)
total_rows = int(cur.fetchall()[0][0])


for i,(itemId,url) in enumerate(data):
    if i < start_index:
        continue 

    if (i+1) % 50 == 0:
        print "updating row #{} out of {}".format(i+1, total_rows)
    HTML = requests.get(url).text
    try:
        condition = str(Selector(text=HTML).xpath("//td[@class='sellerNotesContent']/span[@class='viSNotesCnt']/text()").extract()[0])
        condition = condition.replace("\'","")
    except:
        condition = 'NULL' 
    print i,condition
    SQL = '''
    UPDATE ONLY completed_items as ci
    SET conditiondescription = '{condition}'
    WHERE ci."itemId" = {itemId};
    '''.format(condition=condition,itemId=itemId)    
    cur.execute(SQL)
    conn.commit()
    










    
    
