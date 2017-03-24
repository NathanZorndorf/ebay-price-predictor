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
            #'keywords': '',
            #'CategoryId' : '181194', # vintage electronic keyboards
            'CategoryId'  :  '31388', # digital cameras 
            # https://developer.ebay.com/devzone/finding/CallRef/types/ItemFilterType.html
            # https://developer.ebay.com/devzone/finding/CallRef/extra/fndCmpltdItms.Rqst.tmFltr.nm.html
            'itemFilter': [
                {'name': 'Condition', 'value': 'Used'},
                {'name': 'LocatedIn', 'value': 'US'},
                {'name': 'MinPrice',  'value': '10'}
                {'name': 'ListingType', 'value':'Auction'},
                {'name': 'ListingType', 'value':'AuctionWithBIN'},
                {'name': 'HideDuplicateItems', 'value':'true'},
                {'name': 'SellerBusinessType', 'value' : 'Private'}
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

        # print dic.keys() # ['ack', 'timestamp', 'version', 'searchResult', 'paginationOutput']
        # print dic['searchResult'] # ['item', '_count']
        # print  dic['searchResult']['item'][0].keys() # ['itemId', 'topRatedListing', 'globalId', 'title', 'country', 'primaryCategory', 'autoPay', 'galleryURL', 'shippingInfo', 'location', 'postalCode', 'returnsAccepted', 'viewItemURL', 'sellingStatus', 'paymentMethod', 'isMultiVariationListing', 'condition', 'listingInfo']

        # print sys.getsizeof(dic) # size of default dict + pictureURLLarge is 280 bytes 

        for item in dic['searchResult']['item']:
            print 'listing title:\t\t', item['title']
            print 'listing sale price($):\t', item['sellingStatus']['currentPrice']['value']
            print 'image URL:\t', item['pictureURLLarge'], '\n'
            print ''


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

    except ConnectionError as e:
        print(e)
        print(e.response.dict())



if __name__ == "__main__":
    print 'connecting to database...'
	print("Finding samples for SDK version %s" % ebaysdk.get_version())
	(opts, args) = init_options()
	run(opts)
