import global_const
import requests, json, urlparse, pymongo
import sys, threading, random, time, datetime
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

thread_list=[]
total_count = 0
listing_set = []
scraped_list = set()

#Collates listings from the main city url_list and populates available properties
#such as listing url, price, title, date
def create_page_listings(city_name, city_url, url_list):
    offset = global_const.OFFSET #maximum offset
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
        scrape_thread = threading.Thread(target=run_population_thread, args=(url, city_url, url_list))
        thread_list.append(scrape_thread)
        offset -= 100
    for thread in thread_list:
        thread.daemon = True
        thread.start()
    for thread in thread_list:
        thread.join()
    print len(scraped_list), "listings newly added from this scraping session"
    print len(url_list), "total historical listings available for the", city_name, "shadow"

def run_population_thread(url, city_url, url_list):
    thread_name = threading.current_thread().name
    listings = []
    doc = send_request(url)
    # print url
    sys.stdout.write(url + '\n')
    spider = create_spider(doc)
    populate_from_search_page(spider, listings, city_url, url_list)
    listing_count = 0
    for listing in listings:
        populate_from_listing_page(listing, global_const.city_table)
        sys.stdout.write("Page scraped: " + listing.url + '\n')
        listing_count += 1
    #print thread_name, ":", listing_count, "listings scraped"

#Initalize listing with fields that can be retrieved from search page
def populate_from_search_page(spider, listings, city_url, url_list):
    global total_count
    global listing_set
    global scraped_list
    thread_name = threading.current_thread().name
    try:
        listing_spiders = spider.find_all(class_='row')
        #Reverse the list so the oldest listing on each page is appended first
        listing_spiders.reverse()
        lock = threading.Lock()
        with lock:
            total_count += listing_spiders.__len__()
            sys.stdout.write("Running total of listings present on shadow site : " + str(total_count) + "\n")
        for listing_spider in listing_spiders:
            #Create a new listing object for urls not already present in database
            url = get_listing_url(listing_spider, city_url)
            if url not in url_list:
                scraped_list.add(url)
            url_list.add(url)
            listing = global_const.Listing()
            try:
                listing.url = url
                listing.description = get_listing_name(listing_spider)
                listing.price = get_listing_price(listing_spider)
                listings.append(listing)
            except Exception, e:
                sys.stdout.write("Error: {}".format(e) + '\n')
                sys.stdout.write("Listing not added to list: " + listing.url + '\n')
    except Exception, e:
        sys.stdout.write("Error: {}".format(e) + '\n')

#Populates remaining fields that require entry into the listing link
#and cannot be grabbed from the search page
def populate_from_listing_page(listing, collection):
    listing_url = listing.url
    doc = send_request(listing_url)
    #Place a delay of up to 5 seconds between each request + processing time
    random_delay()
    spider = create_spider(doc)
    if spider == None:
        sys.stdout.write("Info, listing page could not be found: " + listing_url + '\n')
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
            sys.stdout.write("Error: {}".format(e) + '\n')

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
        sys.stdout.write("Pages id(s) error: " + listing.url + '\n')
    except Exception as e:
        sys.stdout.write("Error: {}".format(e) + '\n')

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
        sys.stdout.write("Info, address not present: " + listing.url + '\n')

def get_listing_url(spider, city_url):
    link_tag = spider.find('a', href=True)
    url = urlparse.urljoin(city_url, link_tag['href'])
    return url

def get_listing_name(spider):
    try:
        name = spider.find(class_='hdrlnk').get_text()
    except:
        sys.stdout.write("Warning, listing description retrieval not possible" + '\n')
    return name

def get_listing_date(spider, listing):
    date = ""
    try:
        time = spider.find(class_='postinginfo').time
        date = time.get_text().split(" ")[0]
    except:
        sys.stdout.write("Warning, listing either removed or expired: " + listing.url + '\n')
    listing.date = date

def populate_bed_and_bath(spider, listing):
    try:
        group = spider.find(class_='attrgroup').find_all('span')[0]
        group = group.find_all('b')
        listing.bed = group[0].string
        listing.bath = group[1].string
    except:
        sys.stdout.write("Info, bed and bath info not present: " + listing.url + '\n')

def populate_footage(spider, listing):
    try:
        group = spider.find(class_='attrgroup').find_all('span')[1]
        listing.footage = group.find('b').string
    except AttributeError as e:
        listing.footage = ""
    except:
        sys.stdout.write("Info, square footage not present: " + listing.url + '\n')

def populate_lat_and_long(spider, listing):
    try:
        map = spider.find(id='map')
        listing.lat = map['data-latitude']
        listing.longitude = map["data-longitude"]
    except:
        sys.stdout.write("Info, lat/long not present: " + listing.url + '\n')

def get_city_and_zipcode(listing):
        if listing.lat and listing.longitude:
            try:
                #url = global_const.GOOGLE_GEOCODER + listing.lat + "," + listing.longitude
                url = global_const.MAPBOX_GEOCODER_START + listing.longitude + "," + listing.lat + global_const.MAPBOX_GEOCODER_END
                response = send_request(str(url))
                geocode_json = json.loads(response) #Response comes in as string from request
                populate_city_and_zipcode(geocode_json, listing)
            except Exception as e:
                sys.stdout.write("Error: {}".format(e) + '\n')
                sys.stdout.write("Warning, geocoding failed: " + listing.url + '\n')

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
    global scraped_list
    try:
        listing.database_input_date = datetime.datetime.utcnow()
        collection.insert_one(listing.__dict__)
    except pymongo.errors.DuplicateKeyError as e:
        sys.stdout.write("Warning, listing already exists in db and will have details replaced: " + listing.url + '\n')
        collection.update_one({"post_id": str(listing.post_id)}, {"$set": listing.__dict__})
    except Exception, e:
        sys.stdout.write("Error: {}".format(e) + '\n')
        sys.stdout.write("Failure to add item to db: " + listing.url + '\n')

def send_request(url):
    result = ""
    try:
        response = requests.get(url, headers=global_const.headers)
        if not response.status_code // 100 == 2:
            return "Error: Unexpected response {}".format(response)
        if 'Content-Encoding' in response.headers and response.headers['Content-Encoding'] == "gzip": #Decode
            result = response.content
        else:
            result = response.text
    except requests.exceptions.RequestException as e:
        sys.stdout.write("Error: {}".format(e) + '\n')
    return result

def create_spider(doc):
    try:
        spider = BeautifulSoup(doc, 'html.parser')
    except AttributeError as e:
        return None
    return spider

def random_delay():
    sleep_time = random.randint(0,3)
    time.sleep(sleep_time) #sleep at most 3 seconds after each response to each listing page