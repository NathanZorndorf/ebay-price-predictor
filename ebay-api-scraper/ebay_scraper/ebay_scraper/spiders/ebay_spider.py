import scrapy
# from items import EbayScraperItem
import items
import psycopg2
import logging
from scrapy.utils.log import configure_logging

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
        urls = [str(url) for itemId,url,listingType in cur.fetchall()]
        num_urls_total = len(urls)
        urls = urls[self.url_start_index:]         # limit scraping to only the indeces we care about. we could do this in SQL, and we should make that change later


        # ---- HARDCODED FOR DEV/TESTING PURPOSES ---- #
        # urls = [
        #     'http://www.ebay.com/itm/Nikon-D750-24-3-MP-Digital-SLR-Camera-Black-Body-Only-Used-/222447550032',
        #     'http://www.ebay.com/itm/Canon-EOS-5D-Mark-II-24-105mm-Lens-and-Camera-Bag-/272592893520',
        #     'http://www.ebay.com/itm/DJI-Inspire-1-V1-0-4K-X3-Camera-and-3-Axis-Gimbal-Drone-Quadcopter-Extras-/302257646034',
        #     'http://www.ebay.com/itm/Samsung-NX-NX1-28-2-MP-Digital-Camera-Black-Kit-w-50-200mm-OIS-Lens-/222445254405',
        #     'http://www.ebay.com/itm/Panasonic-AJ-HDC27F-2-3-HD-DVCPRO-Varicam-Video-Camera-Camcorder-w-Viewfinder-/142319141084',
        #     'http://www.ebay.com/itm/High-Speed-Pin-Registered-Super-8-Cartridge-Camera-Very-Rare-Logmar-Wilcam-/252816500866',
        #     'http://www.ebay.com/itm/Carl-Zeiss-Planar-T-80mm-f-2-AF-Lens-Contax-645-camera-/332163276401',
        #     'http://www.ebay.com/itm/DJI-Mavic-Pro-Folding-Drone-4K-Stabilized-Camera-Active-Track-Avoidance-GPS-/252821264198',
        #     'http://www.ebay.com/itm/Nikon-D40-6-1MP-Digital-SLR-Camera-Black-Kit-w-AF-S-DX-18-55mm-Lens-/262891375158'
        # ]

        # THIS CAN RETURN A GENERATOR or "LIST OF REQUESTS"
        # https://doc.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.start_requests
        for i,url in enumerate(urls):
            logging.debug("scraping #{} out of {} urls.".format(i+self.url_start_index, num_urls_total))
            yield scrapy.Request(url=url, callback=self.parse) # after yielding the request, scrapy will go and download the url, and then call the callback function



    def parse(self, response):

        item = items.EbayScraperItem()


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

        # Item duration
        duration_xpath = "//span[@class='titleValueFont'][4]/text()"
        item['duration'] = str(response.xpath(duration_xpath).extract_first())

        # Start price 
        bid_count = response.xpath("//a[@id='vi-VR-bid-lnk']/span[1]/text()").extract_first()
        bid_history_url = response.xpath("//a[@id='vi-VR-bid-lnk']/@href").extract_first()
        if bid_history_url != None and bid_count != 0: # this prevents us from making an unecessary requests if there is no startPrice (because no bids)
            request = scrapy.Request(bid_history_url, callback=self.parse_start_price)
            request.meta['item'] = item # save item to meta attribute of request 
            return request # download response from request, then enter callback function self.parse_start_price with response 
        else: # if the item had 0 bids             
            startPrice = response.xpath("//span[@id='prcIsum']/text()").extract_first()
            startPrice = float(startPrice.split('$')[1].replace(',',''))
            item['startPrice'] = startPrice
            return item # don't request a new url, just send item to pipeline.py




    def parse_start_price(self, response):
        item = response.meta['item'] # grab item attribute from response 
        start_price_xpath = "//tr[@id='viznobrd']/td[@class='contentValueFont'][1]/text()"        
        startPrice = response.xpath(start_price_xpath).extract_first(default='NULL')
        if startPrice != 'NULL':
            startPrice = float(startPrice.split('$')[1].replace(',',''))

        item['startPrice'] = startPrice

        return item # Return item because all information has been gathered into item as this point 


        