GECODOING_URL = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
OFFSET = 2400
#Periodically update the operating system and broswer version number
#Create array of different user agents to be randomly selected from
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel MAC OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
IP_CHECK_ADDR = "https://www.atagar.com/echo.php"
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
SOCKS_PORT = 8080
SOCKS_HOST = "222.114.148.47"

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
