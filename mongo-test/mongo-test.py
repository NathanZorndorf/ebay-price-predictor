from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)

# get a database
db = client['posts-database']

# get a collection called posts
posts = db['posts']

# sample data
post = {
	"author": "Mike",
	"text": "My first blog post!",
	"tags": ["mongodb", "python", "pymongo"],
	"date": datetime.datetime.utcnow()
}

# insert a document into a collection
# when a document is inserted, a special key, "_id" 
# is automatically added if the document doesn't contain the "_id" key. "_id" must be unique. 
post_id = posts.insert_one(post).inserted_id 
print post_id

# After inserting the first document, the posts collection has actually been created on the server. 
# verify by listing all the collections in the database 
print db.collection_names(include_system_collections=False) 

