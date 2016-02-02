import global_const, user_agent, spider
import urllib2, time, multiprocessing, urlparse, lxml, csv

user_agent.create_user_agent()

#Goes to the main city page
city_url = "https://sfbay.craigslist.org/search/eby/apa"
listings = []
listings = spider.create_page_listings(city_url, listings)

#Add keys to create header for csv file
listing_dict = []
listing = listings[0]
listing = listing.__dict__
listing = listing.keys()
listing_dict.append(listing)

for listing in listings:
    spider.populate_fields_present_on_listing_page(listing)
    dict_list = listing.__dict__
    val_list = dict_list.values()
    listing_dict.append(val_list)

with open("craigslist.csv", "wb") as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerows(listing_dict)

#Save the pages_url object to resuse on consecutive occasions to check if listing needs to be updated or for reposts

#Run queries in parallel
#def download(url, start):
 #   return (time.time() - start, urllib.urlopen(url).read(), time.time()-start)
