import sys
sys.path.insert(0, '/Users/Naekid/Desktop/capstone-DSI-5/ebay-price-predictor/bh_photo_scraper/bh_photo_scraper/')

import scrapy
from scrapy.spiders import CrawlSpider
import psycopg2
import logging

from items import BhPhotoDigitalCameraItem
from bs4 import BeautifulSoup

class DigitalCameraSpider(scrapy.Spider):
    name = "digital_camera_spider"


    def start_requests(self):

        url = 'https://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/N/4288586282' # Digital Cameras
        # url = 'https://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/pn/1/N/4288586282?via=js'

        # Get number of pages
        yield scrapy.Request(url=url, callback=self.get_num_pages)
        
        # yield scrapy.Request(url=url, callback=self.parse, meta={'num_pages':num_pages})



    def parse(self, response):

        num_pages = response.meta['num_pages']
        page_num = response.meta['page_num'] + 1

        brands = response.xpath("//a[@class='c5']/span[1]/text()").extract()
        titles = response.xpath("//a[@class='c5']/span[2]/text()").extract()        
        ids = response.xpath("//span[1]/span[@class='sku']/text()").extract()
        # XPATH does not work entirely for prices, use beautifulsoup instead
        # retail_prices = response.xpath("//span[@class='price bold sixteen c7']/text()").extract()
        soup = BeautifulSoup(response.body, 'lxml')
        prices = [float(price.get_text().strip().strip('$').replace(',','')) \
                for price in soup.find_all('span','price')]



        for i in range(len(brands)):
            item = BhPhotoDigitalCameraItem()
            item['brand'] = brands[i].strip()
            item['title'] = titles[i].strip()
            item['bh_id'] = ids[i].strip()

            # NOTE: Sometimes, the price field is not there, hopefully this only occurs when 
            # the item is  at the bottom of the page, otherwise the brands,titles,ids,prices  
            # elements will be out of sync.
            try:
                item['retail_price'] = prices[i] 
            except IndexError as e: 
                print e
                # item['retail_price'] = None
            

            yield item



        # when done processing items, move onto next page 
        if page_num < num_pages:
            next_url = 'https://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/pn/{}/N/4288586282?via=js'.format(page_num)
            yield scrapy.Request(next_url, callback=self.parse, meta={'num_pages':num_pages,'page_num':page_num})



    def get_num_pages(self, response):
        logging.debug('Made it here!')
        num_pages = response.xpath("//p[@class='pageNuber']/text()").extract_first().strip().split()[-1]
        page_num = 0 # start at page 1
        yield scrapy.Request(url=response.url, callback=self.parse, dont_filter=True, meta={'num_pages':num_pages,'page_num':page_num})


