#!/usr/bin/env python

import global_const, user_agent, spider

user_agent.create_user_agent()
print spider.send_request("https://www.atagar.com/echo.php").read() #Get ip address

#Goes to the main city page
city_name = "Chicago"
city_url = "https://chicago.craigslist.org/search/chc/apa"

city_table = spider.create_mongo_collection(city_name)
listings = spider.create_page_listings(city_name, city_url)

for listing in listings:
    spider.populate_from_listing_page(listing, city_table)

#Parallelize
