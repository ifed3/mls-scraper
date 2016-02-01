import global_const, user_agent, spider
import urllib2, time, multiprocessing, urlparse, lxml, csv

BASE_URL = global_const.BASE_URL

user_agent.create_user_agent()

print urllib2.urlopen("https://www.atagar.com/echo.php").read()

print spider.send_request("https://www.dnsleaktest.com/results.html").read()

#print spider.send_request('http://icanhazip.com')

user_agent.tor_process.kill()

# #Goes to the main city page
# city_code = None
# listings = []
# listings = spider.create_page_listings(city_code, listings)
#
# #Add keys to create header for csv file
# listing_dict = []
# listing = listings[0]
# listing = listing.__dict__
# listing = listing.keys()
# listing_dict.append(listing)
#
# for listing in listings:
#     spider.populate_fields_present_on_listing_page(listing)
#     dict_list = listing.__dict__
#     val_list = dict_list.values()
#     listing_dict.append(val_list)
#
# with open("craigslist.csv", "wb") as myfile:
#     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#     wr.writerows(listing_dict)

#Save the pages_url object to resuse on consecutive occasions to check if listing needs to be updated or for reposts

#Run queries in parallel
#def download(url, start):
 #   return (time.time() - start, urllib.urlopen(url).read(), time.time()-start)
