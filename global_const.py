GOOGLE_GEOCODER = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
MAPBOX_GEOCODER_START = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
MAPBOX_GEOCODER_END = ".json?access_token=pk.eyJ1IjoidGNnc2NyYXBlIiwiYSI6ImNpa2oxeTh2ejA1Z2Z2MGttYnBjNzI4bXcifQ.Ftfs_hYahINOthUfdWIXMQ"
OFFSET = 2400
#Periodically update the operating system and broswer version number
#Create array of different user agents to be randomly selected from
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel MAC OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
IP_CHECK_ADDR = "https://www.atagar.com/echo.php"
MONGO_HOST = '192.168.8.2'
MONGO_PORT = 27017
SOCKS_PORT = 0
SOCKS_HOST = ""

headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'User-agent': USER_AGENT
            }

class Listing:
    def __init__(self):
        self.url = ""
        self.description = ""
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
        self.post_id=""
        self.repost_of=""
        self.database_input_date=""

#initialize global variables
def init():
    global shadow_db
    shadow_db = ""
    global city_table
    city_table = ""
    global city_name
    city_name = ""
    global city_url
    city_url = ""
    global csv_directory
    csv_directory = ""
