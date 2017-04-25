# Ebay Listing Optimizer through Machine Learning
![Mock up of a web app that would use the research I've outlined in this report.](.capstone-technical-report/images/buyers_guide_example.png)

If you've ever bought something on Ebay, you know that it can be difficult to know if a particular listing is a good deal or not. And if you're selling, it can be hard to determine which options will draw bidders to your auction. What if there was a way to increase the likelihood that you would sell your listing on ebay, just by swapping a few keywords in your title? What if there was a way to filter listings for only the best deals?

To investiage these questions, I dug into actual ebay data and built a machine learning system to help sellers make more sales on ebay, and alert shoppers to the best deals so they can make smarter buying decisions and save money.

In this report, I'll discuss the decisions I made and show revelant code blocks and visualizations that describe my modeling process. 

# 1. Web Scraping, Data Cleaning, Data Piping
Using the Ebay API and a related Python wrapper, I collected data for 100,000 completed listings in the "Digital Camera" category for the past 3 months, and stored the data in a table within a postgres database.
![Sample of rows for a listing in Postgres database](.capstone-technical-report/images/completed_items_v2.png)

The data included features like

- Listing Title
- Seller Feedback Score
- Free Shipping Available
- Listing End Price

However, I suspected that start price and condition descriptions would be important features. Since they were not available through the API, I created a scraper with Scrapy to fetch URLs from my database, scrape the start price and condition, and store it back into my database.

Now that I had the necessary data in my database, I could import it into Python.
![Subset of columns of my data](.capstone-technical-report/images/example_dataframe.png)





# 2. Data Pre-Processing

# 3. Data Visualization

# 4. Feature Engineering

# 5. Modeling & Model Validation

# 6. Application
