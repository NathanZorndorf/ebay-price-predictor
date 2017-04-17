# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import logging


class BhPhotoDigitalCameraPipeline(object):

	def __init__(self, postgres_host,postgres_user,postgres_db,postgres_table):
		self.postgres_host=postgres_host
		self.postgres_user=postgres_user
		self.postgres_db=postgres_db
		self.postgres_table=postgres_table

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
		for field in item.fields:
			item.setdefault(field, 'NULL')

		# SQL = '''
		# UPDATE {table_name}
		# SET "Brand"='{brand}',
		# 	"Model"='{model}',
		# 	"Retail Price"={retail_price},
		# 	"Body Only"={body_only},
		# 	"Kit"={kit},
		# 	"Has Lens"={has_lens},
		# 	"Lens"='{lens}',
		# 	"B&H Id"='{bh_id}',
		# 	"Title"='{title}'
		# ;
		# '''.format( table_name=self.postgres_table, 
		# 			brand=item['brand'],
		# 			model=item['model'],
		# 			retail_price=item['retail_price'],
		# 			body_only=item['body_only'],
		# 			kit=item['kit'],
		# 			has_lens=item['has_lens'],
		# 			lens=item['lens'],
		# 			bh_id=item['bh_id'],
		# 			title=item['title']					
		# 	) 
		

		insert_statement = '''INSERT INTO {table_name} (%s) VALUES %s;'''.format(table_name=self.postgres_table)

		keys = ['Brand','Title','Retail Price','B&H Id']
		keys = ['"{}"'.format(key) for key in keys] 
		values = (item['brand'],item['title'],item['retail_price'],item['bh_id'])	

		SQL = self.cur.mogrify(insert_statement, (psycopg2.extensions.AsIs(','.join(keys)), values))

		try:
			self.cur.execute(SQL) # execute SQL, and commit changes 
			self.conn.commit()
		except:
			logging.debug('Error with executing SQL statement.\n SQL = {}'.format(SQL))
			self.conn.rollback()


		return item


	def close_spider(self, spider):
		self.conn.close()
		self.cur.close()


