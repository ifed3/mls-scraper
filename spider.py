import global_const, user_agent
import requests, json, gzip, lxml, urlparse, pymongo
import sys, threading, random, time, datetime
from bs4 import BeautifulSoup
from StringIO import StringIO
from multiprocessing.dummy import Pool as ThreadPool

reload(sys)
sys.setdefaultencoding('utf-8')

thread_list=[]

#Collates listings from the main city url_list and populates available properties
#such as listing url, price, title, date
def create_page_listings(city_name, city_url, url_list):
    offset = global_const.OFFSET #maximum offset
    global listing_count
    listing_count = 0
    url_query = ""
    if "nh" in city_url:
        url_query = city_url.split("?")[1]
        city_url = city_url.split("?")[0]
    while offset > -1:
        url = city_url + "?s=" + str(offset)
        if url_query:
            url = url + "&" + url_query
        if offset < 100: #main search page
            url = city_url
            if url_query:
                url = city_url + "?" + url_query
        scrape_thread = threading.Thread(target=run_population_thread, args=(url, city_url, url_list, listing_count))
        thread_list.append(scrape_thread)
        offset -= 100
    for thread in thread_list:
        thread.daemon = True
        thread.start()
    for thread in thread_list:
        thread.join()
    print len(url_list), "total listings available"

def run_population_thread(url, city_url, url_list, listing_count):
    listings = []
    doc = send_request(url)
    print url
    spider = create_spider(doc)
    populate_from_search_page(spider, listings, city_url, url_list)
    lock = threading.Lock()
    thread_name = threading.current_thread().name
    for listing in listings:
        populate_from_listing_page(listing, global_const.city_table)
        listing_count += 1
        print thread_name, ":", listing_count, "listings scraped"

#Initalize listing with fields that can be retrieved from search page
def populate_from_search_page(spider, listings, city_url, url_list):
    listing = ""
    try:
        listing_spiders = spider.find_all(class_='row')
        #Reverse the list so the oldest listing on each page is appended first
        listing_spiders.reverse()
        for listing_spider in listing_spiders:
            #Create a new listing object only when a url does not exist in the database
            url = get_listing_url(listing_spider, city_url)
            if url not in url_list:
                url_list.add(url)
                listing = global_const.Listing()
                listing.url = url
                listing.description = get_listing_name(listing_spider)
                listing.price = get_listing_price(listing_spider)
                listings.append(listing)
    except Exception, e:
        print "Error: {}".format(e)
        print listing.url

#Populates remaining fields that require entry into the listing link
#and cannot be grabbed from the search page
def populate_from_listing_page(listing, collection):
    listing_url = listing.url
    doc = send_request(listing_url)
    #Place a delay of up to 5 seconds between each request + processing time
    random_delay()
    spider = create_spider(doc)
    if spider == None:
        print "Error, listing page could not be found:", listing_url
    else:
        get_listing_date(spider, listing)
        populate_page_ids(spider, listing)
        spider = spider.find(class_='mapAndAttrs')
        populate_bed_and_bath(spider, listing)
        populate_footage(spider, listing)
        populate_lat_and_long(spider, listing)
        get_address(spider, listing)
        get_city_and_zipcode(listing)
        try:
            add_listing_to_database(collection, listing)
        except Exception, e:
            print "Error: {}".format(e)

def populate_page_ids(spider, listing):
    try:
        scripts = spider.find_all("script")
        id_group = ""
        for script in scripts:
            if "pID" in script.string:
                id_group = script.string
                break
        id_group = id_group.split(";")
        for text in id_group:
            if "pID" in text:
                listing.post_id = long(text.split('"')[1])
            if "repost" in text:
                listing.repost_of = text.split("= ")[1]
    except AttributeError as e:
        print "Error relating to page id(s): ", listing.url
    except Exception as e:
        print "Error: {}".format(e)

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
        print "Error, address not present:", listing.url

def get_listing_url(spider, city_url):
    link_tag = spider.find('a', href=True)
    url = urlparse.urljoin(city_url, link_tag['href'])
    return url

def get_listing_name(spider):
    name = spider.find(class_='hdrlnk').get_text()
    return name

def get_listing_date(spider, listing):
    date = ""
    try:
        time = spider.find(class_='postinginfo').time
        date = time.get_text().split(" ")[0]
    except:
        print "Error relating to post creation date:", listing.url
    listing.date = date

def populate_bed_and_bath(spider, listing):
    try:
        group = spider.find(class_='attrgroup').find_all('span')[0]
        group = group.find_all('b')
        listing.bed = group[0].string
        listing.bath = group[1].string
    except:
        print "Error, bed and bath info not present:" , listing.url

def populate_footage(spider, listing):
    try:
        group = spider.find(class_='attrgroup').find_all('span')[1]
        listing.footage = group.find('b').string
    except AttributeError as e:
        listing.footage = ""
    except:
        print "Error, square footage not present:", listing.url

def populate_lat_and_long(spider, listing):
    try:
        map = spider.find(id='map')
        listing.lat = map['data-latitude']
        listing.longitude = map["data-longitude"]
    except:
        print "Error, lat/long not present:", listing.url

def get_city_and_zipcode(listing):
        if listing.lat and listing.longitude:
            try:
                #url = global_const.GOOGLE_GEOCODER + listing.lat + "," + listing.longitude
                url = global_const.MAPBOX_GEOCODER_START + listing.longitude + "," + listing.lat + global_const.MAPBOX_GEOCODER_END
                response = send_request(str(url))
                geocode_json = json.loads(response) #Response comes in as string from request
                populate_city_and_zipcode(geocode_json, listing)
            except Exception as e:
                print "Error: {}".format(e)
                print "Error, geocoding failed:", listing.url

def populate_city_and_zipcode(geocode_json, listing):
    # results = geocode_json['results'][0]
    # for result in results['address_components']:
    #     if result['types'][0] == "locality":
    #         listing.city = result['long_name']
    #         continue
    #     if result['types'][0] == "postal_code":
    #         listing.zipcode = result['long_name']
    #         break
    results = geocode_json['features']
    for result in results:
        if "place" in result['id']:
            listing.city = result['text']
            continue
        if "postcode" in result['id']:
            listing.zipcode = result['text']
            break

def add_listing_to_database(collection, listing):
    try:
        listing.database_input_date = datetime.datetime.utcnow()
        collection.insert_one(listing.__dict__)
    except Exception, e:
        print "Error: {}".format(e)
        print "Failure to add item to db:", listing.url

def send_request(url):
    result = ""
    try:
        response = requests.get(url, headers=global_const.headers)
        if not response.status_code // 100 == 2:
            return "Error: Unexxpected response {}".format(response)
        if 'Content-Encoding' in response.headers and response.headers['Content-Encoding'] == "gzip": #Decode
            result = response.content
        else:
            result = response.text
    except requests.exceptions.RequestException as e:
        print "Error: {}".format(e)
    return result

def create_spider(doc):
    try:
        spider = BeautifulSoup(doc, 'lxml') #Use the lxml html parser
    except AttributeError as e:
        return None
    return spider

def random_delay():
    sleep_time = random.randint(0,5)
    time.sleep(sleep_time) #sleep at most 5 seconds after each response to each listing page
