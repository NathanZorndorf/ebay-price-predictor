# Based on http://www.eamonnbell.com/blog/2015/10/05/the-right-way-to-use-requests-in-parallel-in-python/

import sys
import requests
from multiprocessing import Pool
import psycopg2
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import math

start_index = input('Which index are you starting at?')

def request_url(data):	
    (itemId,url) = data
    print 'parsing itemId:{} from url {}'.format(itemId, url)
    HTML = requests.get(url).text
    try:
        condition = str(Selector(text=HTML).xpath("//td[@class='sellerNotesContent']/span[@class='viSNotesCnt']/text()").extract()[0])
        condition = condition.replace("\'","")
    except:
        condition = 'NULL' 
    
    return (itemId,condition)


# connect to database
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



# get itemId, url from table
SQL = '''
SELECT ci."itemId", ci."viewItemURL" 
FROM completed_items as ci;
'''
cur.execute(SQL)
data = [(int(itemId),str(url)) for itemId,url in cur.fetchall()]

data_len = int(math.ceil(len(data)/100.))
# print data[:5]
print '# of entries in completed_items:',data_len
print 'start_index:',start_index
# sys.exit()

#------- INSERT SCRAPY HERE 


# break up multi-threaded processing into chunks, so we don't load entire data set into memory 
for i in range(data_len):
    print i
    if i < start_index:
    	continue
    else:
		try:
		    temp_data = data[i*100:i*100+100]
		except:
		    temp_data = data[i*100:]

		pool = Pool(processes=3)
		item_condition_list = pool.map(request_url, temp_data)

		# for every chunk of data, update postresql table
		for itemId,condition in item_condition_list:
		    SQL = '''
		    UPDATE ONLY completed_items as ci
		    SET conditiondescription = '{condition}'
		    WHERE ci."itemId" = {itemId};
		    '''.format(condition=condition,itemId=itemId)    
		    cur.execute(SQL)
		    conn.commit()    


cur.close()
conn.close()






















#----------------------- TEST -----------------------#
# import requests
# from multiprocessing import Pool


# url_list = [ (222447550032,
#   'http://www.ebay.com/itm/Nikon-D750-24-3-MP-Digital-SLR-Camera-Black-Body-Only-Used-/222447550032'),
#  (272592893520,
#   'http://www.ebay.com/itm/Canon-EOS-5D-Mark-II-24-105mm-Lens-and-Camera-Bag-/272592893520'),
#  (302257646034,
#   'http://www.ebay.com/itm/DJI-Inspire-1-V1-0-4K-X3-Camera-and-3-Axis-Gimbal-Drone-Quadcopter-Extras-/302257646034'),
#  (222445254405,
#   'http://www.ebay.com/itm/Samsung-NX-NX1-28-2-MP-Digital-Camera-Black-Kit-w-50-200mm-OIS-Lens-/222445254405'),
#  (142319141084,
#   'http://www.ebay.com/itm/Panasonic-AJ-HDC27F-2-3-HD-DVCPRO-Varicam-Video-Camera-Camcorder-w-Viewfinder-/142319141084'),
#  (252816500866,
#   'http://www.ebay.com/itm/High-Speed-Pin-Registered-Super-8-Cartridge-Camera-Very-Rare-Logmar-Wilcam-/252816500866'),
#  (332163276401,
#   'http://www.ebay.com/itm/Carl-Zeiss-Planar-T-80mm-f-2-AF-Lens-Contax-645-camera-/332163276401'),
#  (252821264198,
#   'http://www.ebay.com/itm/DJI-Mavic-Pro-Folding-Drone-4K-Stabilized-Camera-Active-Track-Avoidance-GPS-/252821264198'),
# ]

# url_list = [url for itemId,url in url_list]

# def internet_getter(url):
# 	s = requests.Session()

# 	print url
# 	s.get(url).text


# pool = Pool(processes=3)
# pool_outputs = pool.map(internet_getter,
#                         url_list)

# pool.close()
# pool.join()

# print pool_outputs