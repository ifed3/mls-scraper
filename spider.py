import global_const, user_agent
import urllib2, json, gzip, lxml, urlparse
import sys, multiprocessing, random, time
from bs4 import BeautifulSoup
from StringIO import StringIO

pages_url = set()

reload(sys)
sys.setdefaultencoding('utf-8')

base_url = ""

#Collates listings from the main city pages_url and populates available properties
#such as listing url, price, title, date
def create_page_listings(city_url, listings):
    base_url = city_url
    offset = global_const.OFFSET #maximum offset
    while offset > -1:
        url = city_url + "?s=" + str(offset)
        if offset < 100: #main search page
            url = city_url
        print url
        doc = send_request(url)
        spider = create_spider(doc)
        populate_from_search_page(spider, listings)
        offset -= 100
    print len(global_const.pages_url)
    return listings

def populate_from_search_page(spider, listings):
    listing = global_const.Listing()
    try:
        listing_spiders = spider.find_all(class_='row')
        for listing_spider in listing_spiders:
            listing = global_const.Listing()
            listing.url = get_listing_url(listing_spider)
            if listing.url not in pages_url:
                pages_url.add(listing.url)
                listing.prop_name = get_listing_name(listing_spider)
                listing.date = get_listing_date(listing_spider)
                listing.price = get_listing_price(listing_spider)
                listings.append(listing)
    except Exception, e:
        print str(e)
        print listing.url

#This function populates other fields that require entry into the listing link
#and cannot be grabbed from the search page
def populate_from_listing_page(listing):
    listing_url = listing.url
    doc = send_request(url)
    random_delay()
    spider = create_spider(doc)
    if spider == None:
        print "Listing could not be found :", listing_url
    else:
        spider = spider.find(class_='mapAndAttrs')
        populate_bed_and_bath(spider, listing)
        populate_footage(spider, listing)
        populate_lat_and_long(spider, listing)
        get_address(spider, listing)
        get_city_and_zipcode(listing)

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

def get_listing_url(spider):
    link_tag = spider.find('a', href=True)
    url = urlparse.urljoin(base_url, link_tag['href'])
    return url

def get_listing_name(spider):
    name = spider.find(class_='hdrlnk').get_text()
    return name

def get_listing_date(spider):
    time_tag = spider.time
    datetime = time_tag['datetime']
    date = datetime.split(" ")[0]
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
        print urllib2.urlopen("https://www.atagar.com/echo.php").read() #Get ip address
        doc = urllib2.urlopen(url)
        encoding = doc.info().getheader('Encoding')
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
