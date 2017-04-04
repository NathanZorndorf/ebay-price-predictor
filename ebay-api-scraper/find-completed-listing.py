import os
import sys
from optparse import OptionParser
import psycopg2
from psycopg2.extensions import AsIs
from collections import OrderedDict
import datetime
import pprint 

numArgs = len(sys.argv)
if numArgs < 1 or numArgs > 7:
    print 'ERROR: Not enough arguments. Please input "host",user",dbname","tablename",minPrice,maxPrice as arguments.'
    sys.exit()

(host, user, dbname, TABLE_NAME,minPrice,maxPrice) = tuple(sys.argv[1:])

pagesToQuery = int(input('Enter number of pages to query:'))
entriesPerPage = int(input('Enter number of entries per page to query:'))
pageStart = int(input('Enter page number to start at:'))

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))


import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError

def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",action="store_true", dest="debug", default=False,help="Enabled debugging [default: %default]")
    parser.add_option("-y", "--yaml",dest="yaml", default='./ebay.yaml',help="Specifies the name of the YAML defaults file. [default: %default]")
    parser.add_option("-a", "--appid",dest="appid", default=None,help="Specifies the eBay application id to use.")

    (opts, args) = parser.parse_args()

    return opts, args


def run(opts, pagesToQuery=1, entriesPerPage=1, pageStart=1):

    # --- set up query parameters ; COULD NOT GET THIS TO HAVE ANY AFFECT
    # endTimeFrom = '2017-03-30 11:10:00'
    # endTimeTo   = '2017-04-02 12:00:00'
    # endTimeFrom = datetime.datetime.strptime(endTimeFrom, "%Y-%m-%d %H:%M:%S").isoformat() + '.000Z'
    # endTimeTo   = datetime.datetime.strptime(endTimeTo, "%Y-%m-%d %H:%M:%S").isoformat() + '.000Z'
    # print 'endTimeFrom:',endTimeFrom
    # print 'endTimeTo:',endTimeTo


    # ------ CONNECT TO POSTGRES DATABSE ----- #
    # dbname='ebay'
    # user='nathan'
    # host='localhost'
    # TABLE_NAME = 'completed_items_15230_31388'

    try:
        conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
        print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
    except:
        print "ERROR: Unable to connect to the database." 
        sys.exit("Check database connection settings and try again.")

    cur = conn.cursor()

    # ------------ QUERY EBAY ---------------- #
    try:
        api = finding(debug=opts.debug, appid=opts.appid,config_file=opts.yaml, warnings=True)

        for pageNum in range(pageStart, pageStart+pagesToQuery+1): 

            api_request = {
                # 'keywords': 'camera',
                'categoryId'  :  '15230', # 15230 : Film cameras     
                'categoryId'  :  '31388', # 31388 : Digital cameras     
                'itemFilter': [
                    {'name': 'LocatedIn', 'value': 'US'},
                    {'name': 'Currency', 'value':'USD'},

                    {'name': 'Condition', 'value': 'Used'},
                    {'name': 'MinPrice',  'value': minPrice},
                    {'name': 'MaxPrice',  'value': maxPrice},

                    # {'name': 'ListingType', 'value':'Auction'},
                    # {'name': 'ListingType', 'value':'AuctionWithBIN'},
                    {'name': 'ListingType', 'value':'FixedPrice'},
                    # {'name': 'SoldItemsOnly', 'value':'true'},

                    {'name': 'HideDuplicateItems', 'value':'true'},

                    # {'name': 'SellerBusinessType', 'value' : 'Private'},
                    
                    # {'name': 'EndTimeFrom', 'value': endTimeFrom},
                    # {'name': 'EndTimeTo',   'value': endTimeTo}
                ],                
                'outputSelector': [
                  'PictureURLLarge',
                  'SellerInfo',
                  'UnitPriceInfo'
                ],
                'paginationInput': {
                    'entriesPerPage': entriesPerPage, # max = 100
                    'pageNumber': pageNum    # execute the call with subsequent values for this field 
                },                
                'sortOrder' : 'EndTimeSoonest'
            }

            response = api.execute('findCompletedItems', api_request)

            dic = response.dict()

            # if failure, print detail s
            if dic['ack'] != 'Success':
                print 'ack: ',dic['Ack']
                print 'error message: ',dic['errorMessage']

            if pageNum == 1:
                # print dic
                totalPages = dic['paginationOutput']['totalPages']
                totalEntries = dic['paginationOutput']['totalEntries']
                # _count = dic['searchResult']['_count']
                print 'Total Pages = {}'.format(totalPages)
                print 'Total Entries = {}'.format(totalEntries)


            # print "dic['searchResult']['item'][0]:{}".format(dic['searchResult']['item'][0])
            # pprint.pprint(dic['searchResult']['item'][0])

            # ------ STORE EBAY DATA IN DICTIONARY ------ #
            ebay_data_dict = OrderedDict()

            timestamp = dic['timestamp'] # Example : '2017-03-25T01:58:10.520Z'
            ebay_data_dict['timestamp'] = timestamp 

            for entryNum in range(len(dic['searchResult']['item'])):
                for key1,val1 in dic['searchResult']['item'][entryNum].iteritems():
                    if type(val1) is dict:
                        for key2,val2 in val1.iteritems():
                            if type(val2) is dict:
                                for key3,val3 in val2.iteritems():
                                    # print '{}.{}.{} : {}'.format(key1,key2,key3,val3)
                                    key = '.'.join([key1,key2,key3])
                                    val = val3
                                    ebay_data_dict[key] = val
                            else:
                                # print '{}.{} : {}'.format(key1,key2,val2)
                                key = '.'.join([key1,key2])
                                val = val2
                                ebay_data_dict[key] = val
                    else:
                        # print '{} : {}\n'.format(key1, val1)
                        key = key1
                        val = val1
                        ebay_data_dict[key] = val

                # remove entries we don't need
                bad_keys = [ \
                "searchResult.item.attribute", \
                "searchResult.item.attribute.value",\
                "searchResult.item.attribute.name", \
                "searchResult.item.discountPriceInfo.originalRetailPrice_currencyId", \
                "searchResult.item._distance"
                "searchResult.item.galleryInfoContainer.galleryURL._gallerySize",\
                "searchResult.item.listingInfo.convertedBuyItNowPrice._currencyId", \
                "sellingStatus.convertedCurrentPrice.value", \
                "sellingStatus.convertedCurrentPrice._currencyId",  \
                "sellingStatus.currentPrice._currencyId", \
                "listingInfo.buyItNowPrice._currencyId", \
                "listingInfo.convertedBuyItNowPrice._currencyId", \
                "shippingInfo.shippingServiceCost._currencyId", \
                "listingInfo.convertedBuyItNowPrice.value", \
                "galleryPlusPictureURL", \
                "storeInfo.storeURL", \
                "storeInfo.storeName", \
                "productId._type",\
                "productId.value", 
                "charityId",\
                "discountPriceInfo.soldOnEbay", \
                "discountPriceInfo.pricingTreatment", \
                "discountPriceInfo.originalRetailPrice._currencyId", \
                "discountPriceInfo.originalRetailPrice.value", \
                "discountPriceInfo.soldOffEbay", \
                ]
                for key in bad_keys:
                    if key in ebay_data_dict.keys():
                        ebay_data_dict.pop(key)

                # ------ ENTER EBAY DATA INTO TABLE ----- #
                currentEntryNum = entryNum + pageNum * entriesPerPage
                totalEntriesNum = dic['paginationOutput']['totalEntries']
                # print 'sesarchResult._count:{}'.format(dic['searchResult']['_count'])
                print "inserting item #{} out of {} into table {} in database {}".format(currentEntryNum,totalEntriesNum, TABLE_NAME, dbname)
                # print 'categoryId:'.format(ebay_data_dict['primaryCategory.categoryId'])
                # pprint.pprint(ebay_data_dict)
                keys = ['"{}"'.format(key) for key in ebay_data_dict.keys()] # surround key with quotes
                values = ebay_data_dict.values() # extract values 


                insert_statement = 'INSERT INTO {} (%s) values %s'.format(TABLE_NAME)
                query = cur.mogrify(insert_statement, (AsIs(','.join(keys)), tuple(values)))
                cur.execute(query)
                conn.commit()


        # ------ CLOSE CONNECTION TO DATABSE ----- #
        cur.close()
        conn.close()


    except ConnectionError as e:
        print(e)
        print(e.response.dict())


#-------------------------------#
#------------ MAIN -------------#
#-------------------------------#

if __name__ == "__main__":
    # print 'connecting to database...'
	print("Finding samples for SDK version %s" % ebaysdk.get_version())
	(opts, args) = init_options()
	run(opts, pagesToQuery=pagesToQuery, entriesPerPage=entriesPerPage, pageStart=pageStart)
