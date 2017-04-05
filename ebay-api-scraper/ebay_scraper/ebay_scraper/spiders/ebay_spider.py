import scrapy
# from items import EbayScraperItem
import items
import psycopg2
import logging
from scrapy.utils.log import configure_logging
from pprint import pprint 

class EbaySpider(scrapy.Spider):
    name = "ebay"

    def __init__(self, url_start_index=0, *args, **kwargs):
        super(EbaySpider, self).__init__(*args, **kwargs) # don't know what this does, but saw it in documentation
        self.url_start_index = int(url_start_index)        


    def start_requests(self):  
        


        #--- Connect to ebay database, grab itemId, URL 
        postgres_host = self.crawler.settings.get('POSTGRES_HOST')
        postgres_user = self.crawler.settings.get('POSTGRES_USER')
        postgres_db = self.crawler.settings.get('POSTGRES_DB')
        postgres_table = self.crawler.settings.get('POSTGRES_TABLE')

        conn = psycopg2.connect("dbname={} user={} host={}".format(postgres_db, postgres_user, postgres_host))
        cur = conn.cursor()
        
        # Start scraping at item in database that is furthest back in time
        # That way, we can always pick up scraping where we left off, and even if we put 
        # new data into table, we don't overwrite it in a new scrape. 
        SQL = '''
        SELECT ci."itemId", ci."viewItemURL", ci."listingInfo.listingType"
        FROM {tablename} as ci
        ORDER BY ci."timestamp" ASC; 
        '''.format(tablename=postgres_table)
        cur.execute(SQL)
        urls = [(str(url), listingType) for itemId,url,listingType in cur.fetchall()]
        num_urls_total = len(urls)
        urls = urls[self.url_start_index:]         # limit scraping to only the indeces we care about. we could do this in SQL, and we should make that change later


        # ---- HARDCODED FOR DEV/TESTING PURPOSES ---- #
        # urls = [
            # "http://offer.ebay.com/ws/eBayISAPI.dll?ViewBids&item=192140341983&rt=nc&_trksid=p2047675.l2565"
            # 'http://www.ebay.com/itm/Nikon-D750-24-3-MP-Digital-SLR-Camera-Black-Body-Only-Used-/222447550032',
            # 'http://www.ebay.com/itm/Canon-EOS-5D-Mark-II-24-105mm-Lens-and-Camera-Bag-/272592893520',
            # 'http://www.ebay.com/itm/DJI-Inspire-1-V1-0-4K-X3-Camera-and-3-Axis-Gimbal-Drone-Quadcopter-Extras-/302257646034',
            # 'http://www.ebay.com/itm/Samsung-NX-NX1-28-2-MP-Digital-Camera-Black-Kit-w-50-200mm-OIS-Lens-/222445254405',
            # 'http://www.ebay.com/itm/Panasonic-AJ-HDC27F-2-3-HD-DVCPRO-Varicam-Video-Camera-Camcorder-w-Viewfinder-/142319141084',
            # 'http://www.ebay.com/itm/High-Speed-Pin-Registered-Super-8-Cartridge-Camera-Very-Rare-Logmar-Wilcam-/252816500866',
            # 'http://www.ebay.com/itm/Carl-Zeiss-Planar-T-80mm-f-2-AF-Lens-Contax-645-camera-/332163276401',
            # 'http://www.ebay.com/itm/DJI-Mavic-Pro-Folding-Drone-4K-Stabilized-Camera-Active-Track-Avoidance-GPS-/252821264198',
            # 'http://www.ebay.com/itm/Nikon-D40-6-1MP-Digital-SLR-Camera-Black-Kit-w-AF-S-DX-18-55mm-Lens-/262891375158'
        # ]
        # urls = [("http://www.ebay.com/itm/Canon-EOS-7D-18-0-MP-Digital-SLR-Camera-Black-Body-Only-/192140341983",'Auction')]

        # THIS CAN RETURN A GENERATOR or "LIST OF REQUESTS"
        # https://doc.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.start_requests
        for i,tup in enumerate(urls):
            logging.debug("scraping #{} out of {} urls.".format(i+self.url_start_index, num_urls_total))
            url = tup[0]
            listingType = tup[1]
            yield scrapy.Request(url=url, callback=self.parse, meta={'listingType':listingType}) # after yielding the request, scrapy will go and download the url, and then call the callback function



    def parse(self, response):

        item = items.EbayScraperItem()

        listingType = response.meta['listingType']

        # Item condition
        item_condition_xpath = "//td[@class='sellerNotesContent']/span[@class='viSNotesCnt']/text()"        
        item['conditionDescription'] = str(response.xpath(item_condition_xpath) \
                                            .extract_first(default='NULL') \
                                    ).decode('unicode_escape')  \
                                    .encode('ascii','ignore') \
                                    .replace("\'","") 

        # Item ID
        item_id_xpath = "//div[@id='descItemNumber']/text()"
        item['itemId'] = int(response.xpath(item_id_xpath).extract_first())
        

        if listingType == 'Auction' or listingType == 'AuctionWithBIN':
            bid_count = int(response.xpath("//a[@id='vi-VR-bid-lnk']/span[1]/text()").extract_first())
            bid_history_url = response.xpath("//a[@id='vi-VR-bid-lnk']/@href").extract_first()

            if bid_history_url != None:

                if bid_count > 0: # this prevents us from making an unecessary requests if there is no startPrice (because no bids)                

                    logging.debug('bid_history_url = {}'.format(bid_history_url))
                    logging.debug('bid_count = {}'.format(bid_count))

                    return scrapy.Request(url=bid_history_url, callback=self.parse_start_price, meta={'item':item})

                else: # if the item had 0 bids             
                    item['startPrice'] = float(str(response.xpath("//span[@class='notranslate vi-VR-cvipPrice']/text()").extract_first()).split('$')[1].replace(',',''))
                    item['duration'] = 'NULL'
                    item['endPrice'] = 'NULL'
                    return item # don't request a new url, just send item to pipeline.py

        else: # 'FixedPrice' or 'StoreInventory'
            item['endPrice'] = float(str(response.xpath("//span[@id='prcIsum']/text()").extract_first()).split('$')[1].replace(',',''))
            item['startPrice'] = 'NULL'
            item['duration'] = 'NULL'
            return item



    def parse_start_price(self, response):

        item = response.meta['item'] # grab item attribute from response 


        # item end price - I don't think we need this, because the endPrice is given in findCOmpletedItems

        # end_price_xpath = "//div[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td[@class='BHctBidVal']/text()"
        # item['endPrice'] = float(str(response.xpath(end_price_xpath).extract_first()).split('$')[1].replace(',',''))
        item['endPrice'] = 'NULL'

        # Item duration
        duration_xpath = "//span[@class='titleValueFont'][4]/text()"
        item['duration'] = str(response.xpath(duration_xpath).extract_first()) \
                            .decode('unicode_escape') \
                            .encode('ascii','ignore') \
                            .split('\r')[0]


        # Item start price - ebay has (at least) 2 different types of HTML pages for the startPrice info
        # try grabbing first xpath 
        start_price_xpath = "//tr[@id='viznobrd']/td[@class='contentValueFont'][1]/text()"        
        startPrice = response.xpath(start_price_xpath).extract_first(default='NULL') 
        
        logging.debug("startPrice = {}".format(startPrice))

        if startPrice != 'NULL': # the first x path worked 
            startPrice = float(startPrice.split('$')[1].replace(',',''))
            item['startPrice'] = startPrice
            return item

        # Try grabbing the second xpath if the first xpath didn't work
        start_price_xpath = "//table[@id='w2-w3-w0-w0']"

        for item in response.xpath(start_price_xpath).extract():
            logging.debug('item in response.xpath() SECOND PATH = {}'.format(item))

        startPrice = response.xpath(start_price_xpath).extract_first(default='NULL') 
        if startPrice != 'NULL': # if the 2nd xpath worked...
            logging.debug('url = {}'.format(response.url))
            logging.debug('SECOND XPATH => startPrice = {}'.format(startPrice))
            startPrice = startPrice.split('$')[-1] # take the last entry in the table, which is something like: 80.0023 Mar 2017 at 1:23:58PM PDT            
            startPrice = '.'.join([startPrice.split('.')[0], startPrice.split('.')[1][:2]]) # take numbers before decimal and concatenate with 2 digits after decimal
            startPrice = startPrice.replace(',','')
            item['startPrice'] = float(startPrice)
            return item


        logging.debug('response.url = {}'.format(response.url))
        logging.debug('startPrice = {}'.format(startPrice))
        logging.debug('itemId = {}'.format(item['itemId']))

        # if the first 2 xpaths didn't work... DEBUG
        item['startPrice'] = 'NULL'            
        return item 


        