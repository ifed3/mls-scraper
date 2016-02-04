#!/usr/bin/env python

import global_const, user_agent, spider
import csv, json, sys, os
import pymongo
from pymongo import MongoClient

def request_user_input():
    global city_name
    city_name = raw_input("Enter location name: ")
    global city_url
    city_url = raw_input("Enter url referring to location (eg. for Chicago, https://chicago.craigslist.org/search/chc/apa): ")
    global csv_directory
    csv_directory = raw_input("Enter folder to save results to csv file: ")

def create_database(city_name):
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.shadow_market
    collection = db[city_name]
    collection.create_index([('url', pymongo.ASCENDING)], unique=True)
    return collection

def retrieve_urls_from_database(collection):
    url_list = set()
    urls = collection.find(projection={'url':True, '_id':False})
    if urls.count() > 0:
        for url in urls:
            url_list.add(url['url'])
    return url_list

def scrape_site(city_table, city_url, city_name, url_list):
    listings = spider.create_page_listings(city_name, city_url, url_list)
    for listing in listings:
        spider.populate_from_listing_page(listing, city_table)

def write_csv_file(csv_directory, city_name, city_table):
    #Retrieve all documents from db (without the id field)
    documents = city_table.find(projection={'_id':False})
    #Convert json from db to csv
    #JSON represents flat object, if that changes in the future, this code will not be entirely functional
    csv_filename = os.path.join(csv_directory, city_name + "_shadow.csv")
    print csv_filename
    with open(csv_filename, "wb+") as myfile:
        #Use dict writer in csv creation to ensure desired order
        fieldnames = ["city", "description", "url", "footage", "zipcode",
                        "bed", "bath", "date", "lat", "longitude", "address", "price"]
        wr = csv.DictWriter(myfile, fieldnames=fieldnames)
        wr.writeheader()
        for document in documents:
            wr.writerow(document)

request_user_input()
user_agent.create_user_agent()
print spider.send_request("https://www.atagar.com/echo.php").read() #Get ip address
city_table = create_database(city_name)
url_list = retrieve_urls_from_database(city_table)
scrape_site(city_table, city_url, city_name, url_list)
write_csv_file(csv_directory, city_name, city_table)

# #Goes to the main city page
# #Use for gui aspect
# # city_name = open(sys.argv[0])
# # city_url = open(sys.argv[1])
# # csv_directory = open(sys.argv[2])
# https://chicago.craigslist.org/search/chc/apa
# /Users/ifed3/Documents/Development/Repositories/shadow-mls-crawler

#Parallelize
