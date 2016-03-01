#!/usr/bin/env python

import global_const, spider
import csv, os
import pymongo
from pymongo import MongoClient

def create_database():
    client = MongoClient()
    client = MongoClient(global_const.MONGO_HOST, global_const.MONGO_PORT)
    db = client.shadow_market
    return db

def create_datatable(database, city_name):
    collection = database[city_name]
    collection.create_index([('post_id', pymongo.ASCENDING)], unique=True)
    return collection

def retrieve_urls_from_database(collection):
    url_list = set()
    urls = collection.find(projection={'url':True, '_id':False})
    if urls.count() > 0:
        for url in urls:
            url_list.add(url['url'])
    return url_list

def scrape_site(city_table, city_url, city_name, url_list):
    spider.create_page_listings(global_const.city_name, global_const.city_url, url_list)

def write_csv_file(csv_directory, city_name, city_table):
    #Retrieve all documents from db (without the id field)
    documents = global_const.city_table.find(projection={'_id':False})
    #Convert json from db to csv
    #JSON represents flat object, if that changes in the future, this code will not be entirely functional
    csv_filename = os.path.join(global_const.csv_directory, global_const.city_name + " Shadow.csv")
    with open(csv_filename, "wb+") as myfile:
        #Use dict writer in csv creation to ensure desired order
        fieldnames = ["city", "description", "url", "footage", "zipcode", "bed", "bath",
                    "date", "lat", "longitude", "address", "price", "post_id", "repost_of", "database_input_date"]
        wr = csv.DictWriter(myfile, fieldnames=fieldnames)
        wr.writeheader()
        for document in documents:
            wr.writerow(document)

def set_up():
    global_const.init()
    print spider.send_request(global_const.IP_CHECK_ADDR) #Get ip address
    global_const.shadow_db = create_database()

def main():
    try:
        global_const.city_table = create_datatable(global_const.shadow_db, global_const.city_name)
        url_list = retrieve_urls_from_database(global_const.city_table)
        scrape_site(global_const.city_table, global_const.city_url, global_const.city_name, url_list)
        write_csv_file(global_const.csv_directory, global_const.city_name, global_const.city_table)
    except Exception, e:
        print str(e)
    finally:
        print "Scraping exited"
        write_csv_file(global_const.csv_directory,
                        global_const.city_name, global_const.city_table)
