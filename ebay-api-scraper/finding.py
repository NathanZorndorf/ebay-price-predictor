# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
from optparse import OptionParser
from pprint import pprint 

# The line below will add this file's parent directory 
# to the search path for python modules
sys.path.insert(0, '%s/../' % os.path.dirname(__file__)) # /Users/Naekid/Desktop/capstone-DSI-5/ebaysdk-python/samples

from common import dump # ebay SDK support file 

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
                      dest="yaml", default='/Users/Naekid/Desktop/capstone-DSI-5/ebay-price-predictor/ebay-api-scraper/ebay.yaml',
                      help="Specifies the name of the YAML defaults file. [default: %default]")
    parser.add_option("-a", "--appid",
                      dest="appid", default=None,
                      help="Specifies the eBay application id to use.")

    (opts, args) = parser.parse_args()
    return opts, args



def find_completed_item(opts):

    try:
        api = finding(debug=opts.debug, appid=opts.appid,config_file=opts.yaml, warnings=True)

        api_request = {
            'keywords': 122431840128,
        }

        response = api.execute('findCompletedItems', api_request)

        dic = response.dict()

        pprint(dic)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())



def run(opts):

    try:
        api = finding(debug=opts.debug, appid=opts.appid,config_file=opts.yaml, warnings=True)

        api_request = {
            'keywords': 'camera',
            'CategoryId' : '31388',
            'itemFilter': [
                {'name': 'Condition', 'value': 'Used'},
                {'name': 'LocatedIn', 'value': 'US'},
                {'name': 'MinPrice',  'value': '10'}
            ],
             'paginationInput': {
                'entriesPerPage': '1',
                'pageNumber': '1'    
            },
            'sortOrder': 'PricePlusShippingLowest',
        }

        response = api.execute('findCompletedItems', api_request)

        dic = response.dict()

        # print dic.keys() # ['ack', 'timestamp', 'version', 'searchResult', 'paginationOutput']
        # print dic['searchResult'] # ['item', '_count']
        # print  dic['searchResult']['item'][0].keys() # ['itemId', 'topRatedListing', 'globalId', 'title', 'country', 'primaryCategory', 'autoPay', 'galleryURL', 'shippingInfo', 'location', 'postalCode', 'returnsAccepted', 'viewItemURL', 'sellingStatus', 'paymentMethod', 'isMultiVariationListing', 'condition', 'listingInfo']

        for item in dic['searchResult']['item']:
            print 'listing title:\t\t', item['title']
            print 'listing sale price($):\t', item['sellingStatus']['currentPrice']['value']


        # dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def run_unicode(opts):

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, warnings=True)

        api_request = {
            'keywords': u'Kościół',
        }

        response = api.execute('findItemsAdvanced', api_request)
        for i in response.reply.searchResult.item:
            if i.title.find(u'ś') >= 0:
                print("Matched: %s" % i.title)
                break

        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def run2(opts):
    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml)

        response = api.execute('findItemsByProduct',
                               '<productId type="ReferenceID">53039031</productId><paginationInput><entriesPerPage>1</entriesPerPage></paginationInput>')

        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def run_motors(opts):
    api = finding(siteid='EBAY-MOTOR', debug=opts.debug, appid=opts.appid, config_file=opts.yaml,
                  warnings=True)

    api.execute('findItemsAdvanced', {
        'keywords': 'tesla',
    })

    if api.error():
        raise Exception(api.error())

    if api.response_content():
        print("Call Success: %s in length" % len(api.response_content()))

    print("Response code: %s" % api.response_code())
    print("Response DOM: %s" % api.response_dom())

    dictstr = "%s" % api.response_dict()
    print("Response dictionary: %s..." % dictstr[:250])

if __name__ == "__main__":
    print("Finding samples for SDK version %s" % ebaysdk.get_version())
    (opts, args) = init_options()
    find_completed_item(opts)
    # run(opts)
    # run2(opts)
    # run_motors(opts)
    # run_unicode(opts)
