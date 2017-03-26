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
 


