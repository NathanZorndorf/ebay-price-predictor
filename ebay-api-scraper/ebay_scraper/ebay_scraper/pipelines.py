# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2

class EbayPostgresPipeline(object):

	def __init__(self, postgres_host,postgres_user,postgres_db,postgres_table):
		self.postgres_host=postgres_host
		self.postgres_user=postgres_user
		self.postgres_db=postgres_db
		self.postgres_table=postgres_table

	'''
	The settings attribute is set in the base Spider class after the spider is
	 initialized. If you want to use the settings before the initialization 
	 (e.g., in your spider’s __init__() method), you’ll need to override the 
	 from_crawler() method.
	 '''
	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			postgres_host=crawler.settings.get('POSTGRES_HOST'),
			postgres_user=crawler.settings.get('POSTGRES_USER'),
			postgres_db=crawler.settings.get('POSTGRES_DB'),
			postgres_table=crawler.settings.get('POSTGRES_TABLE'),
		)	


	def open_spider(self, spider):
		self.conn = psycopg2.connect("dbname={} user={} host={}".format(self.postgres_db,   \
																		self.postgres_user, \
																		self.postgres_host) \
		)
		self.cur = self.conn.cursor()


	def process_item(self, item, spider):
		'''store data into postgres database 

		'''

		SQL = '''
		UPDATE ONLY {table_name} as ci
		SET conditiondescription = '{condition}'
		WHERE ci."itemId" = {itemId};
		'''.format( table_name=self.postgres_table, 
		condition=item['condition'], 
		itemId = item['itemId'] 
		) 

		self.cur.execute(SQL) # execute SQL, and commit changes 
		self.conn.commit()

		return item


	def close_spider(self, spider):
		self.conn.close()
		self.cur.close()





