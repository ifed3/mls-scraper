#Configuring the crawler to respect the Craigslist robots.txt permissions
#Time module is included to automatically updated robots.txt permissions

import global_const, time, urlparse, robotparser

rp = robotparser.RobotFileParser()
rp.set_url(urlparse.urljoin(global_const.BASE_URL, "robots.txt"))
rp.read()
rp.modified()

PATHS = [
    '/',
    '/eba/apa/'
]

for n, path in enumerate(PATHS):
    print
    #Calculate the difference between the current time and last time robots.txt was fetched
    age = int(time.time() - rp.mtime())
    print 'age:', age, 
    if age > 36000: #check every 10 hours
        print "Re-capturing robots.txt permissions"
        rp.read()
        rp.modified()
    else:
        print
    print '%6s : %s' % (rp.can_fetch(global_const.USER_AGENT, path), path)
    time.sleep(1)

