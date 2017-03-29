import scrapy
import psycopg2

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
        
        SQL = '''
        SELECT ci."itemId", ci."viewItemURL" 
        FROM {tablename} as ci;
        '''.format(tablename=postgres_table)
        cur.execute(SQL)
        urls = [str(url) for itemId,url in cur.fetchall()]
        # limit scraping to only the indeces we care about
        # we could do this in SQL, and we should make that change later
        urls = urls[self.url_start_index:]


        # ---- HARDCODED ---- #
        # urls = [
        #     'http://www.ebay.com/itm/Nikon-D750-24-3-MP-Digital-SLR-Camera-Black-Body-Only-Used-/222447550032',
        #     'http://www.ebay.com/itm/Canon-EOS-5D-Mark-II-24-105mm-Lens-and-Camera-Bag-/272592893520',
        #     'http://www.ebay.com/itm/DJI-Inspire-1-V1-0-4K-X3-Camera-and-3-Axis-Gimbal-Drone-Quadcopter-Extras-/302257646034',
        #     'http://www.ebay.com/itm/Samsung-NX-NX1-28-2-MP-Digital-Camera-Black-Kit-w-50-200mm-OIS-Lens-/222445254405',
        #     'http://www.ebay.com/itm/Panasonic-AJ-HDC27F-2-3-HD-DVCPRO-Varicam-Video-Camera-Camcorder-w-Viewfinder-/142319141084',
        #     'http://www.ebay.com/itm/High-Speed-Pin-Registered-Super-8-Cartridge-Camera-Very-Rare-Logmar-Wilcam-/252816500866',
        #     'http://www.ebay.com/itm/Carl-Zeiss-Planar-T-80mm-f-2-AF-Lens-Contax-645-camera-/332163276401',
        #     'http://www.ebay.com/itm/DJI-Mavic-Pro-Folding-Drone-4K-Stabilized-Camera-Active-Track-Avoidance-GPS-/252821264198'
        # ]

        # THIS CAN RETURN A GENERATOR or "LIST OF REQUESTS"
        # https://doc.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.start_requests
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Handle response 
    def parse(self, response):
        item_condition_xpath = "//td[@class='sellerNotesContent']/span[@class='viSNotesCnt']/text()"
        item_id_xpath = "//div[@id='descItemNumber']/text()"
        # use XPath to get condition.
        # Also removes unicode characters, and single quote character. 
        conditionDescription = str(response.xpath(item_condition_xpath) \
                                            .extract_first(default='NULL') \
                                    ).decode('unicode_escape')  \
                                    .encode('ascii','ignore') \
                                    .replace("\'","") 
        
        itemId = int(response.xpath(item_id_xpath).extract_first())

        parsed_items = {
            'itemId' : itemId,
            'condition':conditionDescription,
        }

        return parsed_items



        