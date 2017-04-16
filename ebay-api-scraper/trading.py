# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
import datetime
from optparse import OptionParser
import psycopg2
import time
sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

from common import dump

import ebaysdk
from ebaysdk.utils import getNodeText
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

from pprint import pprint


host = 'localhost'
user = 'nathan'
dbname = 'ebay' 
tablename = 'category_specifics'


numArgs = len(sys.argv)
if numArgs != 2:
    print 'Incorrect number of input arguments'
    sys.exit()

offset = sys.argv[1]


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
    parser.add_option("-p", "--devid",
                      dest="devid", default=None,
                      help="Specifies the eBay developer id to use.")
    parser.add_option("-c", "--certid",
                      dest="certid", default=None,
                      help="Specifies the eBay cert id to use.")

    (opts, args) = parser.parse_args()
    return opts, args



def getItem(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid)

        try:
            conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
            print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
        except:
            print "ERROR: Unable to connect to the database." 
            sys.exit("Check database connection settings and try again.")

        cur = conn.cursor()

        #----------- GRAB ALL ITEM IDs IN TABLE ----------#        
        query = '''SELECT ci."itemId" 
        FROM category_specifics as ci 
        ORDER BY ci."Model" ASC
        OFFSET {offset};'''.format(offset=offset) # 4745

        cur.execute(query)  
        item_ids = cur.fetchall() 

        for i,itemId in enumerate(item_ids[:]):

            itemId = itemId[0] # itemId is a tuple
            print 'Updating item #{} out of {}'.format(i+1, len(item_ids))
            print 'calling getItem for itemID:{}'.format(itemId)

            api_request = {
                'itemID':itemId,
                'IncludeItemSpecifics':1,
            }

            try:
                response = api.execute('GetItem', api_request)
            except ConnectionError as e:
                print(e)
                print(e.response.dict())
                continue

            dic = response.dict()

            # pprint(dic) # debug 

            allowed_columns = ['Type','Brand','MPN','Series','Model',\
                                'Megapixels','Optical Zoom','Features',\
                                'Color','Bundled Items','Connectivity',\
                                'Battery Type','Manufacturer Warranty',\
                                'Screen Size','Digital Zoom']
            newDict = {}
            try:
                if not isinstance(dic['Item']['ItemSpecifics']['NameValueList'], list): # if only one item 
                    # print dic['Item']['ItemSpecifics']['NameValueList']
                    name = dic['Item']['ItemSpecifics']['NameValueList']['Name']
                    if name in allowed_columns:
                        value = dic['Item']['ItemSpecifics']['NameValueList']['Value']
                        newDict[name] = value

                else:
                    for nameValueDict in dic['Item']['ItemSpecifics']['NameValueList']:
                        # print nameValueDict
                        name = nameValueDict['Name']
                        if name in allowed_columns:
                            value = nameValueDict['Value']          
                            if isinstance(value, list):
                                value = ','.join(value) # join the lists into a string seperated by commas

                            try:
                                newDict[name] = value.decode('unicode_escape').encode('ascii','ignore')
                            except:
                                print 'Problem with value, could not decode for some reason.'
                                continue

            except KeyError as e: # no item specifics in response 
                print 'No ItemSpecifics field in response.', e
                continue



            keys = ['"{}"'.format(key.decode('unicode_escape').encode('ascii','ignore')) for key in newDict.keys()]  
            insert_statement = '''UPDATE {table_name} SET (%s) = %s WHERE "itemId"={item_id};
                                '''.format(table_name=tablename,
                                            item_id=itemId)
            query = cur.mogrify(insert_statement, (psycopg2.extensions.AsIs(','.join(keys)), tuple(newDict.values())))
            # print query

            try:
                cur.execute(query) # execute SQL, and commit changes 
                conn.commit()
            except:
                print '\nError with executing SQL statement at item #{}, itemId={}.\n'.format(i, itemId)
                print query
                conn.rollback()

            # time.sleep(0.04) # throttle 

    except ConnectionError as e:
        print(e)
        print(e.response.dict())






def getCategorySpecifics(opts):


    try:
        conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
        print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
    except:
        print "I am unable to connect to the database"
        sys.exit()

    cur = conn.cursor()


    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid)

        api_request = {
            'CategoryID':'31388' # Digital Cameras 
        }

        response = api.execute('GetCategorySpecifics', api_request)

        dic = response.dict()

        for item in dic['Recommendations']['NameRecommendation']:
            SQL = 'ALTER TABLE {} ADD COLUMN "{}" TEXT;'.format(tablename, item['Name'])
            execute = raw_input('Execute "{}"? (y/n):'.format(SQL))
            if execute == 'y':
                cur.execute(SQL)
                conn.commit()
                execute = 'n'


    except ConnectionError as e:
        print(e)
        print(e.response.dict())

    cur.close()
    conn.close()


def getAPIAccessRules(opts):


    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid)


        response = api.execute('GetApiAccessRules')

        dic = response.dict()

        pprint(dic)


    except ConnectionError as e:
        print(e)
        print(e.response.dict())



def run(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid)

        api.execute('GetCharities', {'CharityID': 3897})
        dump(api)
        print(api.response.reply.Charity.Name)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def feedback(opts):
    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=False)

        api.execute('GetFeedback', {'UserID': 'tim0th3us'})
        dump(api)

        if int(api.response.reply.FeedbackScore) > 50:
            print("Doing good!")
        else:
            print("Sell more, buy more..")

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def getTokenStatus(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=False)

        api.execute('GetTokenStatus')
        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def verifyAddItem(opts):
    """http://www.utilities-online.info/xmltojson/#.UXli2it4avc
    """

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=False)

        myitem = {
            "Item": {
                "Title": "Harry Potter and the Philosopher's Stone",
                "Description": "This is the first book in the Harry Potter series. In excellent condition!",
                "PrimaryCategory": {"CategoryID": "377"},
                "StartPrice": "1.0",
                "CategoryMappingAllowed": "true",
                "Country": "US",
                "ConditionID": "3000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": "Chinese",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": "tkeefdddder@gmail.com",
                "PictureDetails": {"PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007"},
                "PostalCode": "95125",
                "Quantity": "1",
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_30",
                    "Description": "If you are not satisfied, return the book for refund.",
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingType": "Flat",
                    "ShippingServiceOptions": {
                        "ShippingServicePriority": "1",
                        "ShippingService": "USPSMedia",
                        "ShippingServiceCost": "2.50"
                    }
                },
                "Site": "US"
            }
        }

        api.execute('VerifyAddItem', myitem)
        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def verifyAddItemErrorCodes(opts):
    """http://www.utilities-online.info/xmltojson/#.UXli2it4avc
    """

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=False)

        myitem = {
            "Item": {
                "Title": "Harry Potter and the Philosopher's Stone",
                "Description": "This is the first book in the Harry Potter series. In excellent condition!",
                "PrimaryCategory": {"CategoryID": "377aaaaaa"},
                "StartPrice": "1.0",
                "CategoryMappingAllowed": "true",
                "Country": "US",
                "ConditionID": "3000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": "Chinese",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": "tkeefdddder@gmail.com",
                "PictureDetails": {"PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007"},
                "PostalCode": "95125",
                "Quantity": "1",
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_30",
                    "Description": "If you are not satisfied, return the book for refund.",
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingType": "Flat",
                    "ShippingServiceOptions": {
                        "ShippingServicePriority": "1",
                        "ShippingService": "USPSMedia",
                        "ShippingServiceCost": "2.50"
                    }
                },
                "Site": "US"
            }
        }

        api.execute('VerifyAddItem', myitem)

    except ConnectionError as e:
        # traverse the DOM to look for error codes
        for node in api.response.dom().findall('ErrorCode'):
            print("error code: %s" % node.text)

        # check for invalid data - error code 37
        if 37 in api.response_codes():
            print("Invalid data in request")

        print(e)
        print(e.response.dict())


def uploadPicture(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True)

        pictureData = {
            "WarningLevel": "High",
            "ExternalPictureURL": "http://developer.ebay.com/DevZone/XML/docs/images/hp_book_image.jpg",
            "PictureName": "WorldLeaders"
        }

        api.execute('UploadSiteHostedPictures', pictureData)
        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def uploadPictureFromFilesystem(opts, filepath):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True)

        # pass in an open file
        # the Requests module will close the file
        files = {'file': ('EbayImage', open(filepath, 'rb'))}

        pictureData = {
            "WarningLevel": "High",
            "PictureName": "WorldLeaders"
        }

        api.execute('UploadSiteHostedPictures', pictureData, files=files)
        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def memberMessages(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True)

        now = datetime.datetime.now()

        memberData = {
            "WarningLevel": "High",
            "MailMessageType": "All",
            # "MessageStatus": "Unanswered",
            "StartCreationTime": now - datetime.timedelta(days=60),
            "EndCreationTime": now,
            "Pagination": {
                "EntriesPerPage": "5",
                "PageNumber": "1"
            }
        }

        api.execute('GetMemberMessages', memberData)

        dump(api)

        if api.response.reply.has_key('MemberMessage'):
            messages = api.response.reply.MemberMessage.MemberMessageExchange

            if type(messages) != list:
                messages = [messages]

            for m in messages:
                print("%s: %s" % (m.CreationDate, m.Question.Subject[:50]))

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def getUser(opts):
    try:

        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True, timeout=20, siteid='101')

        api.execute('GetUser', {'UserID': 'sallyma789'})
        dump(api, full=False)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def getOrders(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True, timeout=20)

        api.execute('GetOrders', {'NumberOfDays': 30})
        dump(api, full=False)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def categories(opts):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True, timeout=20, siteid='101')

        callData = {
            'DetailLevel': 'ReturnAll',
            'CategorySiteID': 101,
            'LevelLimit': 4,
        }

        api.execute('GetCategories', callData)
        dump(api, full=False)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())

'''
api = trading(domain='api.sandbox.ebay.com')
api.execute('GetCategories', {
    'DetailLevel': 'ReturnAll',
    'CategorySiteID': 101,
    'LevelLimit': 4,
})
'''

if __name__ == "__main__":
    (opts, args) = init_options()

    print("Trading API Samples for version %s" % ebaysdk.get_version())

    """
    run(opts)
    feedback(opts)
    verifyAddItem(opts)
    getTokenStatus(opts)
    verifyAddItemErrorCodes(opts)
    uploadPicture(opts)
    uploadPictureFromFilesystem(opts, ("%s/test_image.jpg" % os.path.dirname(__file__)))
    memberMessages(opts)
    categories(opts)
    """
    # getUser(opts)
    # getOrders(opts)


    getItem(opts)
    # getCategorySpecifics(opts)
    # getAPIAccessRules(opts)
