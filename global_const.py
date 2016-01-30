BASE_URL = "http://www.craigslist.org/"
EAST_BAY_APT = "search/eby/apa"
GECODOING_URL = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
OFFSET = 2400

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
