import psycopg2
import sys

numArgs = len(sys.argv)
if numArgs < 1 or numArgs > 5:
	print 'ERROR: Not enough arguments. Please input "host",user",dbname","tablename" as arguments.'
	sys.exit()

(host, user, dbname, tablename) = tuple(sys.argv[1:])

# dbname='test-db1'
# tablename='tablename'
# user='nathan'
# host='localhost'

print (host, user, dbname, tablename)

try:
    conn = psycopg2.connect("dbname={} user={} host={}".format(dbname, user, host))
    print '\nConnected to {} with user:{} on host:{}\n'.format(dbname, user, host)
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

cur.execute('''
	CREATE TABLE {tablename} (
	"id" 					SERIAL PRIMARY KEY,
	"timestamp"				TIMESTAMP WITH TIME ZONE,
	"itemId" 				BIGINT,
	"topRatedListing" 		BOOLEAN,
	"globalId"				TEXT,
	"title"					TEXT,
	"subtitle"				TEXT,
	"country"				TEXT,
	
	"primaryCategory.categoryId"		INTEGER,
	"primaryCategory.categoryName"		TEXT,
	"secondaryCategory.categoryId"		TEXT,
	"secondaryCategory.categoryName"	TEXT,
	"pictureURLLarge"					TEXT,
	"galleryURL"						TEXT,
	
	"sellerInfo.feedbackRatingStar"			TEXT,
	"sellerInfo.feedbackScore"				INTEGER,
	"sellerInfo.positiveFeedbackPercent"	DECIMAL,
	"sellerInfo.sellerUserName"				TEXT,
	"shippingInfo.expeditedShipping"					BOOLEAN,
	"shippingInfo.shipToLocations"						TEXT,	
	"shippingInfo.shippingServiceCost.value"			DECIMAL,
	"shippingInfo.oneDayShippingAvailable"				BOOLEAN,
	"shippingInfo.handlingTime"							SMALLINT,
	"shippingInfo.shippingType"							TEXT,
	
	"autoPay"				BOOLEAN,
	"location"				TEXT,
	"postalCode"			INTEGER,
	"returnsAccepted"		BOOLEAN,
	"viewItemURL"			TEXT,
	
	"sellingStatus.currentPrice.value"			DECIMAL,	
	"sellingStatus.bidCount" 					SMALLINT,
	"sellingStatus.sellingState"				TEXT,
	"paymentMethod"								TEXT,
	
	"isMultiVariationListing"	BOOLEAN,
	
	"condition"							TEXT,
	"condition.conditionId"				INTEGER,
	"condition.conditionDisplayName"	TEXT,
	"listingInfo.listingType"			TEXT,
	"listingInfo.gift"					BOOLEAN,
	"listingInfo.bestOfferEnabled"		BOOLEAN,
	"listingInfo.startTime"				TIMESTAMP WITH TIME ZONE,
	"listingInfo.buyItNowAvailable"		BOOLEAN,
	"listingInfo.endTime"				TIMESTAMP WITH TIME ZONE,
	"conditiondescription"				TEXT,
	"startprice"						DECIMAL,
	"listingInfo.buyItNowPrice.value"	DECIMAL,
	"endprice"							DECIMAL
)
'''.format(tablename=tablename))

# cur.execute("SELECT * FROM test;")
# cur.fetchone()


conn.commit()
cur.close()
conn.close()











