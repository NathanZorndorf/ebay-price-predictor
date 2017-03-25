import os
import sys
from optparse import OptionParser
import psycopg2

# The line below will add 
sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

# for path in sys.path:
#   print path

# from common import dump # not sure why this module doesn't load 

import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError

def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enabled debugging [default: %default]")
    parser.add_option("-y", "--yaml",
                      dest="yaml", default='ebay.yaml',
                      help="Specifies the name of the YAML defaults file. [default: %default]")
    parser.add_option("-a", "--appid",
                      dest="appid", default=None,
                      help="Specifies the eBay application id to use.")

    (opts, args) = parser.parse_args()
    return opts, args


def run(opts):

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, warnings=True)

        api_request = {
            'keywords': 'camera',
            #'CategoryId' : '181194', # vintage electronic keyboards
            'CategoryId'  :  '625', # digital cameras 
            # https://developer.ebay.com/devzone/finding/CallRef/types/ItemFilterType.html
            # https://developer.ebay.com/devzone/finding/CallRef/extra/fndCmpltdItms.Rqst.tmFltr.nm.html
            'itemFilter': [
                {'name': 'Condition', 'value': 'Used'},
                {'name': 'LocatedIn', 'value': 'US'},
                {'name': 'MinPrice',  'value': '10'},
                {'name': 'ListingType', 'value':'Auction'},
                # {'name': 'ListingType', 'value':'AuctionWithBIN'},
                {'name': 'HideDuplicateItems', 'value':'true'},
                {'name': 'SellerBusinessType', 'value' : 'Private'},
                {'name': 'Currency', 'value':'USD'}
            ],
            # Use outputSelector to include more information in the response. 
            'outputSelector': [
              'PictureURLLarge',
              'SellerInfo',
              'StoreInfo',
              'UnitPriceInfo'
            ],
            'paginationInput': {
                'entriesPerPage': '1', # max = 100
                'pageNumber': '1'    # execute the call with subsequent values for this field 
            },
            #'sortOrder': 'PricePlusShippingLowest',
        }

        response = api.execute('findCompletedItems', api_request)

        dic = response.dict()

        # print 'size of dict is {}\n'.format(sys.getsizeof(dic)) # size of default dict + pictureURLLarge is 280 bytes 

        # ------ CONNECT TO POSTGRES DATABSE ----- #
        dbname='test-db1'
        user='nathan'
        host='localhost'

        try:
            conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
            print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()

        # ------ STORE EBAY DATA IN TABLE ------ #
        timestamp = dic['timestamp'] # Example : '2017-03-25T01:58:10.520Z'

        for key1,val1 in dic['searchResult']['item'][0].iteritems():
            if type(val1) is dict:
                for key2,val2 in val1.iteritems():
                    if type(val2) is dict:
                        for key3,val3 in val2.iteritems():
                            print '{}.{}.{} : {}'.format(key1,key2,key3,val3)
                            key = '.'.join([key1,key2,key3])
                            insert_sql(key, val3, cur)
                    else:
                        print '{}.{} : {}'.format(key1,key2,val2)
            else:
                print '{} : {}\n'.format(key1, val1)

        # ------ CLOSE CONNECTION TO DATABSE ----- #

        cur.close()
        conn.close()

    except ConnectionError as e:
        print(e)
        print(e.response.dict())

def insert_sql(key,val, cursor):
    cur.execute()
    conn.commit()




if __name__ == "__main__":
    # print 'connecting to database...'
	print("Finding samples for SDK version %s" % ebaysdk.get_version())
	(opts, args) = init_options()
	run(opts)
