# ebay-price-predictor
My capstone for GA DSI 5. Predicts whether a given ebay listing will sell or not, and, if it will sell, and how much it will sell for.

Feature : dataType : data : description : outputSelector

DateTime EBay processed request : dateTime 	: timestamp
Item Title 						: string 	: searchResult.item.title
subtitle of listing 			: string 	: searchResult.item.subtitle
Item URL 						: URI 		: searchResult.item.viewItemURL



Category Id 					:  string 	: searchResult.item.primaryCategory.categoryId
Category Name					:  string  	: searchResult.item.primaryCategory.categoryName
Secondary Category Id			:  string 	: searchResult.item.secondaryCategory.categoryId
Secondary Category Name 		:  string  	: searchResult.item.secondaryCategory.categoryName

Quantity 						: double 	: searchResult.item.unitPrice.quantity
Size, Weight, Volume, Count 	: string 	: searchResult.item.unitPrice.type

listing type 					: token 	: searchResult.item.listingInfo.listingType : string : format type of the listing, such as online auction, fixed price, or advertisement. 
conditionDisplayName 			: string  	: searchResult.item.condition.conditionDisplayName
conditionId 					: int 		: searchResult.item.condition.conditionId


best offer enabled 				: boolean 	: searchResult.item.listingInfo.bestOfferEnabled
BuyItNow Available 				: boolean 	: searchResult.item.listingInfo.buyItNowAvailable
BuyItNow Price 					: double  	: searchResult.item.listingInfo.buyItNowPrice
autoPay 						: boolean 	: searchResult.item.autoPay
Payment Method 					: token 	: searchResult.item.paymentMethod

End Time 						: dateTime 	: searchResult.item.listingInfo.endTime
Start Time 						: dateTime 	: searchResult.item.listingInfo.startTime
Location 						: string 	: searchResult.item.location
Postal Code 					: string 	: searchResult.item.postalCode
country 						: token 	: searchResult.item.country

Shipping Cost 					: double 	: searchResult.item.shippingInfo.shippingServiceCost
Shipping Type 					: token 	: searchResult.item.shippingInfo.shippingType

name of seller's ebay store 	: string 	: searchResult.item.storeInfo.storeName
Seller Info 					: token 	: searchResult.item.sellerInfo.feedbackRatingStar : : SellerInfo
Seller Feedback score 			: long 		: searchResult.item.sellerInfo.feedbackScore
Positive Feedback Percent 		: double 	: searchResult.item.sellerInfo.positiveFeedbackPercent
Seller User Name 				: string 	: searchResult.item.sellerInfo.sellerUserName
Top Rated Seller 				: boolean 	: searchResult.item.sellerInfo.topRatedSeller
Top Rated Listing 				: Boolean 	: searchResult.item.topRatedListing

URL for Gallery Thumbnail Image : URI 		: searchResult.item.galleryURL 
Large Picture URL 				: URI (string) :  searchResult.item.pictureURLLarge
  
CREATE TABLE COMPLETED_ITEMS (
	id 		INTEGER PRIMARY KEY,
	itemId 				BIGINT,
	topRatedListing 	BOOLEAN,
	globalId			TEXT,
	title				TEXT,
	country				TEXT,
	
	primaryCategory.categoryId	I	NTEGER,
	primaryCategory.categoryName	TEXT,
	pictureURLLarge					TEXT,
	galleryURL						TEXT,
	
	sellerInfo.feedbackRatingStar		TEXT,
	sellerInfo.feedbackScore			INTEGER,
	sellerInfo.positiveFeedbackPercent	DECIMAL
	sellerInfo.sellerUserName			TEXT,
	shippingInfo.expeditedShipping					BOOLEAN,
	shippingInfo.shipToLocations					TEXT,
	shippingInfo.shippingServiceCost.value			DECIMAL,
	shippingInfo.oneDayShippingAvailable			BOOLEAN,
	shippingInfo.handlingTime						SMALLINT,
	shippingInfo.shippingType						TEXT,
	
	autoPay				BOOLEAN,
	location			TEXT,
	postalCode			INTEGER,
	returnsAccepted		BOOLEAN,
	viewItemURL			TEXT,
	
	sellingStatus.currentPrice.value		DECIMAL,
	sellingStatus.bidCount SMALLINT,
	sellingStatus.sellingState	TEXT,
	paymentMethod	TEXT,
	
	isMultiVariationListing	BOOLEAN,
	
	condition.conditionId			INTEGER,
	condition.conditionDisplayName	TEXT,
	listingInfo.listingType			TEXT,
	listingInfo.gift				BOOLEAN,
	listingInfo.bestOfferEnabled	BOOLEAN,
	listingInfo.startTime			TIMESTAMP WITH TIME ZONE,
	listingInfo.buyItNowAvailable	BOOLEAN,
	listingInfo.endTime				TIMESTAMP WITH TIME ZONE
)
-- shippingInfo.shippingServiceCost._currencyId	TEXT,
-- 	sellingStatus.currentPrice._currencyId	TEXT,
--	sellingStatus.convertedCurrentPrice._currencyId 
--	sellingStatus.convertedCurrentPrice.value 






CREATE TABLE listings(
	ID INTEGER PRIMARY KEY NOT NULL,
	timestamp TIMESTAMP,
	title TEXT,
	subtitle TEXT,
	viewItemURL TEXT,
	
	primaryCategory.categoryId	STRING,
	primaryCategory.categoryName	STRING,
	secondaryCategory.categoryId		STRING,
	secondaryCategory.categoryName	STRING,
	
	unitPrice.quantity SMALLINT,
	unitPrice.type TEXT,
	
	listingInfo.listingType TEXT,
	conditionDisplayName TEXT,
	condition.conditionId SMALLINT,
	
	listingInfo.bestOfferEnabled BOOLEAN,
	listingInfo.buyItNowAvailable BOOLEAN,
	listingInfo.buyItNowPrice INTEGER,
	autoPay BOOLEAN,
	paymentMethod TEXT,
	
	listingInfo.endTime TIMESTAMP,
	listingInfo.startTime TIMESTAMP,
	location TEXT,
	postalCode TEXT,
	country TEXT,
	
	shippingInfo.shippingServiceCost INTEGER,
	shippingInfo.shippingType TEXT,
	
	storeInfo.storeName 	TEXT,
	sellerInfo.feedbackRatingStar 	TEXT,
	sellerInfo.feedbackScore	
		
);







