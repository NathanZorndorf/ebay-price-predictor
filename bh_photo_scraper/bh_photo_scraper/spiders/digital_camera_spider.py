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
        page_num = response.meta['page_num']

        ids = response.xpath("//span[1]/span[@class='sku']/text()").extract()

        brands = response.xpath("//a[@class='c5']/span[1]/text()").extract()
        titles = response.xpath("//a[@class='c5']/span[2]/text()").extract()        

        if len(brands) != len(titles): # an element in brands is a new-release title, remove it
            for i,brand in enumerate(brands):
                if len(brand.split()) > 1: 
                    brands.pop(i)



        # XPATH does not work entirely for prices, use beautifulsoup instead
        # soup = BeautifulSoup(response.body, 'lxml')
        # prices = [float(price.get_text().strip().strip('$').replace(',','')) \
        #         for price in soup.find_all('span','price')]        


        for i in range(len(brands)):
            item = BhPhotoDigitalCameraItem()
            item['brand'] = brands[i].strip()
            item['title'] = titles[i].strip()            

            # NOTE: Sometimes, the price field is not there, hopefully this only occurs when 
            # the item is  at the bottom of the page, otherwise the brands,titles,ids,prices  
            # elements will be out of sync.
            # item['bh_id'] = ids[i].strip()
            # try:
            #     item['retail_price'] = prices[i] 
            # except IndexError as e: 
            #     print e
                # item['retail_price'] = None
            

            yield item



        # when done processing items, move onto next page 
        if page_num <= num_pages:
            logging.debug('Scraping page {}'.format(page_num))
            next_url = 'https://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/pn/{}/N/4288586282?via=js'.format(page_num)
            yield scrapy.Request(next_url, callback=self.parse, meta={'num_pages':num_pages,'page_num':page_num+1})
        else:
            logging.debug('Should be done scraping..')
            # raise CloseSpider('Done Crawling.')
            yield


    def get_num_pages(self, response):
        logging.debug('Made it here!')
        num_pages = response.xpath("//p[@class='pageNuber']/text()").extract_first().strip().split()[-1]
        page_num = 1 # start at page 1
        yield scrapy.Request(url=response.url, callback=self.parse, dont_filter=True, meta={'num_pages':num_pages,'page_num':page_num+1})


