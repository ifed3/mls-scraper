import global_const, urllib2

#Build user agent properties

#Permits identitty of scraping application to resemeble that of a browser
def create_user_agent():
    urllib2.install_opener(opener())

def opener():
    opener = urllib2.build_opener()
    #urllib2.HTTPHandler(debuglevel=1))
    opener.addheaders = [
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Encoding', 'gzip, deflate, sdch'),
            ('Accept-language', 'en-US,en;q=0.8'),
            ('Connection', 'keep-alive'),
            #Periodically update the operating system and broswer version number
            ('User-agent', 'Mozilla/5.0 (Macintosh; Intel MAC OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36')
            ]
    return opener
