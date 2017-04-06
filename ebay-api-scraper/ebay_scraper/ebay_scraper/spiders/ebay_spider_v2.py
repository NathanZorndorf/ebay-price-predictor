import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
# import items
from items import EbayScraperItem
import psycopg2
import logging
from scrapy.utils.log import configure_logging
from pprint import pprint 

class EbaySpider(CrawlSpider):
	name = "ebay_crawl_spider"

	custom_settings = {
		'POSTGRES_TABLE':"completed_items_v2",
		'AUTOTHROTTLE_TARGET_CONCURRENCY':1,
		'DONWLOAD_DELAY':0.8,
        'ITEM_PIPELINES': {
        	'ebay_scraper.pipelines.EbayPostgresPipeline': 300,
        }
    }


	def __init__(self, url_start_index=0, url_end_index=0, *args, **kwargs):
		super(EbaySpider, self).__init__(*args, **kwargs) # don't know what this does, but saw it in documentation
		self.url_start_index = int(url_start_index)      
		self.url_end_index = int(url_end_index)  


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
		SELECT ci."itemId", ci."viewItemURL"
		FROM {tablename} as ci
		ORDER BY ci."timestamp" DESC; 
		'''.format(tablename=postgres_table)
		cur.execute(SQL)

		urls = [(int(itemId),str(url)) for itemId,url in cur.fetchall()]
		if self.url_end_index == 0: 
			self.url_end_index = len(urls)
		num_urls_total = len(urls)
		urls = urls[self.url_start_index:self.url_end_index]         # limit scraping to only the indeces we care about. we could do this in SQL, and we should make that change later

		for i,(itemId,url) in enumerate(urls):
			logging.debug("scraping #{} out of {} urls.".format(i+self.url_start_index, num_urls_total))
			yield scrapy.Request(url=url, callback=self.parse, meta={'itemId':itemId, 'dont_redirect':True}) # after yielding the request, scrapy will go and download the url, and then call the callback function

		# ---- HARDCODED FOR DEV/TESTING PURPOSES ---- #
		# urls = ["http://www.ebay.com/itm/NIKON-D-DF-16-2-MP-DIGITAL-SLR-CAMERA-SILVER-KIT-AF-S-MICRO-60MM-LENS-/291997000430",
		# 		"http://www.ebay.com/itm/Canon-T3i-Body-And-Kit-/272591253524", 
		# 		"http://www.ebay.com/itm/Fujifilm-FinePix-XP-XP70-16-4MP-Waterproof-Digital-Camera-5X-Optical-Zoom-/112242371882",
		# 		"http://www.ebay.com/itm/Canon-Minolta-and-Pentax-Cameras-2-Bags-9-Lenses-and-Filters-/292024262357"
		# ]
		# for url in urls:
		# 	yield scrapy.Request(url=url, callback=self.parse) # after yielding the request, scrapy will go and download the url, and then call the callback function
	


	def parse(self, response):

		item = EbayScraperItem()
		item['itemId'] = response.meta['itemId']

		# Get condition 
		item['conditionDescription'] = response.xpath("//td[@class='sellerNotesContent']/span[@class='viSNotesCnt']/text()")\
												.extract_first(default='NULL')\
												.encode('ascii','ignore')\
												.replace('\'', '')


		# Scrape bid history URL in order to get startPrice 
		bid_history_url = response.xpath("//a[@id='vi-VR-bid-lnk']/@href").extract_first()
		if bid_history_url != None:
			bid_count = int(response.xpath("//a[@id='vi-VR-bid-lnk']/span[1]/text()").extract_first())
			if bid_count > 0:
				return scrapy.Request(url=bid_history_url, callback=self.parse_start_price, meta={'item':item})
			else:
				item['startPrice'] = 'NULL'
				return item
		else:
			item['startPrice'] = 'NULL'
			return item


	def parse_start_price(self, response):
		
		item = response.meta['item']

		# 1st xpath attempt
		startPrice = response.xpath("//tr[@id='viznobrd']/td[@class='contentValueFont'][1]/text()").extract_first()
		if startPrice != None:
			item['startPrice'] = float(startPrice.split('$')[1])
			return item

		# 2nd xpath attempt 
		# startPrice = response.xpath("//span/span/text()").extract()[-3]	
		bid_history_items = response.xpath("//span/text()").extract()		
		if bid_history_items:
			for i,text in enumerate(bid_history_items):
				if text == 'Starting Price':
					startPrice = bid_history_items[i+1]
					item['startPrice'] = float(startPrice.replace('$',''))
					return item

					

		logging.debug('1ST AND 2ND XPATH DID NOT WORK.\n itemId = {}\n'.format(item['itemId']))
		item['startPrice'] = 'NULL'

		return item
		




