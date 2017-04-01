# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EbayScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    itemId = scrapy.Field(default='NULL')
    conditionDescription = scrapy.Field(default='NULL')
    startPrice = scrapy.Field(default='NULL')
