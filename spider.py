import global_const, user_agent
import urllib2, json, gzip, lxml, urlparse
import sys, multiprocessing, random, time, datetime
from bs4 import BeautifulSoup
from StringIO import StringIO
import pymongo
from pymongo import MongoClient


pages_url = set()

reload(sys)
sys.setdefaultencoding('utf-8')

def create_mongo_collection(city_name):
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.shadow_market
    collection = db[city_name]
    return collection

def add_listing_to_collection(collection, listing):
    collection.insert_one(listing.__dict__)

#Collates listings from the main city pages_url and populates available properties
#such as listing url, price, title, date
def create_page_listings(city_name, city_url):
    listings = []
    offset = global_const.OFFSET #maximum offset
    while offset > -1:
        url = city_url + "?s=" + str(offset)
        if offset < 100: #main search page
            url = city_url
        print url
        doc = send_request(url)
        spider = create_spider(doc)
        populate_from_search_page(spider, listings, city_url)
        offset -= 100
    print len(pages_url)
    return listings

def populate_from_search_page(spider, listings, city_url):
    try:
        listing_spiders = spider.find_all(class_='row')
        #Reverse the list so the oldest listing on each page is appended first
        listing_spiders.reverse()
        for listing_spider in listing_spiders:
            listing = global_const.Listing()
            listing.url = get_listing_url(listing_spider, city_url)
            if listing.url not in pages_url:
                pages_url.add(listing.url)
                listing.description = get_listing_name(listing_spider)
                listing.price = get_listing_price(listing_spider)
                listings.append(listing)
    except Exception, e:
        print str(e)
        print listing.url

#This function populates other fields that require entry into the listing link
#and cannot be grabbed from the search page
def populate_from_listing_page(listing, collection):
    listing_url = listing.url
    doc = send_request(listing_url)
    random_delay()
    spider = create_spider(doc)
    if spider == None:
        print "Listing could not be found :", listing_url
    else:
        listing.date = get_listing_date(spider)
        spider = spider.find(class_='mapAndAttrs')
        populate_bed_and_bath(spider, listing)
        populate_footage(spider, listing)
        populate_lat_and_long(spider, listing)
        get_address(spider, listing)
        get_city_and_zipcode(listing)
        try:
            add_listing_to_collection(collection, listing)
        except Exception, e:
            print str(e)

def get_listing_price(spider):
    try:
        price = spider.find(class_='price').get_text()
    except AttributeError as e:
        price = None
    return price

def get_address(spider, listing):
    try:
        addressTag = spider.find('div', class_='mapaddress')
        address = addressTag.get_text()
        listing.address = address
    except AttributeError as e:
        print "Address error : ", listing.url

def get_listing_url(spider, city_url):
    link_tag = spider.find('a', href=True)
    url = urlparse.urljoin(city_url, link_tag['href'])
    return url

def get_listing_name(spider):
    name = spider.find(class_='hdrlnk').get_text()
    return name

def get_listing_date(spider):
    time = spider.find(class_='postinginfo').time
    date = time.get_text().split(" ")[0]
    return date

def populate_bed_and_bath(spider, listing):
    try:
        group = spider.find(class_='attrgroup').find_all('span')[0]
        group = group.find_all('b')
        listing.bed = group[0].string
        listing.bath = group[1].string
    except:
        print "Bed/bath error :" , listing.url

def populate_footage(spider, listing):
    try:
        group = spider.find(class_='attrgroup').find_all('span')[1]
        listing.footage = group.find('b').string
    except AttributeError as e:
        listing.footage = ""
    except:
        print "Footage error :", listing.url

def populate_lat_and_long(spider, listing):
    try:
        map = spider.find(id='map')
        listing.lat = map['data-latitude']
        listing.longitude = map["data-longitude"]
    except:
        print "Lat/Long Error :", listing.url

def get_city_and_zipcode(listing):
        if listing.lat == "" or listing.longitude == "":
            print "Cannot retrieve city information, no lat or long provided :", listing.url
        else:
            url = global_const.GECODOING_URL + listing.lat + "," + listing.longitude
            response = send_request(url)
            geocode_json = json.load(response)
            populate_city_and_zipcode(geocode_json, listing)

def populate_city_and_zipcode(geocode_json, listing):
    results = geocode_json['results'][0]
    for result in results['address_components']:
        if result['types'][0] == "locality":
            listing.city = result['long_name']
            continue
        if result['types'][0] == "postal_code":
            listing.zipcode = result['long_name']
            break

def send_request(url):
    try:
        #tor_process = user_agent.anonymize()
        doc = urllib2.urlopen(url)
        encoding = doc.info().getheader('Content-Encoding')
        if encoding == "gzip": #Decode
            buffer = StringIO(doc.read())
            doc = gzip.GzipFile(fileobj=buffer)
    except urllib2.URLError as e:
        print e.reason
        return None
    except urllib2.HTTPError as e:
        print e.reason
        print doc.getcode()
        return None
    # finally:
    #     user_agent.stop_tor(tor_process)
    return doc

def create_spider(doc):
    try:
        spider = BeautifulSoup(doc.read(), 'lxml') #Use the lxml html parser
    except AttributeError as e:
        return None
    return spider

def random_delay():
    sleep_time = random.randint(0,5)
    time.sleep(sleep_time) #sleep at most 5 seconds after each response to each listing page
