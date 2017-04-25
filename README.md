# Ebay Listing Optimizer through Machine Learning
![Mock up of a web app that would use the research I've outlined in this report.](.capstone-technical-report/images/buyers_guide_example.png)

If you've ever bought something on Ebay, you know that it can be difficult to know if a particular listing is a good deal or not. And if you're selling, it can be hard to determine which options will draw bidders to your auction. What if there was a way to increase the likelihood that you would sell your listing on ebay, just by swapping a few keywords in your title? What if there was a way to filter listings for only the best deals?

To investiage these questions, I dug into actual ebay data and built a machine learning system to help sellers make more sales on ebay, and alert shoppers to the best deals so they can make smarter buying decisions and save money. In order to do that, I had to create models that could predict if an auction would sell or not (at least one person would bid), and if a listing would sell, how much it would sell for.

In this report, I'll discuss the decisions I made and show revelant code blocks and visualizations that describe my modeling process. 

# 1. Web Scraping, Data Cleaning, Data Piping
Using the Ebay API and a related Python wrapper [https://github.com/timotheus/ebaysdk-python], I collected data for 100,000 completed listings in the "Digital Camera" category for the past 3 months, and stored the data in a table within a postgres database.
![Sample of rows for a listing in Postgres database](.capstone-technical-report/images/completed_items_v2.png)

The data included features like

- Listing Title
- Seller Feedback Score
- Free Shipping Available
- Listing End Price

However, I suspected that start price and condition descriptions would be important features. Since they were not available through the API, I created a scraper with Scrapy to fetch URLs from my database, scrape the start price and condition, and store it back into my database.

Now that I had the necessary data in my database, I could import it into Python.
![Subset of columns of my data](.capstone-technical-report/images/example_dataframe.png)

Taking a look at the end prices, we can see the distribution follows a power law. 
![Price distribution of end prices of data](.capstone-technical-report/images/distribution_of_end_prices_auctions.png)


# 2. Pre-Processing

Pre-processing involved transforming the title text and the condition description as text features into numerical data. I used TF-IDF vectorization for the listing titles, as I wanted to cause unique words, like camera models, to have higher values. For conditions, I used count vectorizer, because I noticed many of the same words used across many different titles, such as "Functional","Like New", and "Scratched." I didn't want to down weight these kinds of words.

I also scaled all predictors to the same range so that I could compare model coefficients to each other directly.  


# 3. Feature Engineering
When I thought about what potential factors could contribute to a particular listing selling or not, I hypothesized that listings on ebay are affected by other similar listings. Specifically, I thought that the start price of auctions listed on ebay at the same time, or listed "concurrently", would affect their respective end prices, and wanted to explore this route.I thought that the current price of each listing at the time of listing might be more influential than the start price, but in the interest of time, I decided to focus on start price.

I defined a listing to be concurrent with another listing if the second was posted before the second ended (without a restriction on the amount of concurrent time needed to qualify as a concurrent listing), and filtering in python. 

In order to filter for "similar listings", I vectorized each listings title using sklearn's `TfidfVectorizer` and then calculated a cosime similarity score for each listing. I took only the top 5 most similar items, or those items with a similarity score greather than 0.95, whichever provided more results. I chose 5 and 0.95 through spot-checking the results for a balance between number of results and accuracy in terms of observed similarity. 

The essense of the code is along the lines of:
```python 
    concurrent_listings_df = auctions_subset[auctions_subset['listingInfo.endTime'].apply(lambda sub_listing_et: listing_st<sub_listing_et)]
    cos_sim_matrix = cosine_similarity(current_listings, concurrent_listings)
    concurrent_similar_listings_df = concurrent_listings_df[concurrent_listings_df['similarity_score']>min_sim_score]
```

After I had the top 5 concurrent, similar listings, I took the median start price, and used that as a feature to my models.


# 5. Modeling & Model Validation



# 6. Application
