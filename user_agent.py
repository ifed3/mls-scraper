import global_const, urllib2
import socks, socket #SocksiPy module
import stem.process #Tor launcher

from stem.util import term

#Build user agent properties

SOCKS_PORT = 7000

#Set up proxy service
socks.setdefaultproxy(socks.SOCKS5, 'localhost', SOCKS_PORT)
socket.socket = socks.socksocket

#Configre Tor startup for anonymous scraping
def print_boostrap_lines(line):
    if "Bootstrapped " in line:
        print(term.format(line, term.Color.BLUE))

def start_tor():
    print "Starting Tor:\n"
    tor_process = stem.process.launch_tor_with_config(
        config = {
        'SocksPort': str(SOCKS_PORT),
        'ExitNodes': '{us}', #Make country exit code match search location
        },
        init_msg_handler = print_boostrap_lines,
    )

#Avoid DNS leaks by performing DNS resolution via the socket
def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

socket.getaddrinfo = getaddrinfo

#Permits identitty of scraping application to resemeble that of a browser
def create_user_agent():
    urllib2.install_opener(opener())

def opener():
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
    #urllib2.HTTPHandler(debuglevel=1))
    opener.addheaders = [
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Encoding', 'gzip, deflate, sdch'),
            ('Accept-language', 'en-US,en;q=0.8'),
            ('Connection', 'keep-alive'),
            ('User-agent', global_const.USER_AGENT)
            ]
    return opener
