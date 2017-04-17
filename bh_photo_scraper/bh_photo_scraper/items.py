# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BhPhotoDigitalCameraItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    retail_price = scrapy.Field()
    body_only = scrapy.Field()
    kit = scrapy.Field()
    has_lens = scrapy.Field()
    lens = scrapy.Field()
    bh_id = scrapy.Field()
    title = scrapy.Field()