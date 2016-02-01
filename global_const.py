BASE_URL = "http://www.craigslist.org/"
EAST_BAY_APT = "search/eby/apa"
GECODOING_URL = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
OFFSET = 2400
#Periodically update the operating system and broswer version number
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel MAC OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"

class Listing:
    def __init__(self):
        self.url = ""
        self.prop_name = ""
        self.date = ""
        self.city = ""
        self.zipcode = ""
        self.footage = ""
        self.bed = ""
        self.bath = ""
        self.price = ""
        self.lat = ""
        self.longitude = ""
        self.address = ""
