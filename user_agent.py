import global_const
import urllib2, ssl
import socks, socket #SocksiPy module
# import stem.process #Tor launcher

# from stem.util import term

SOCKS_PORT = global_const.SOCKS_PORT
PROXY_IP = global_const.SOCKS_HOST

def anonymize():
    set_proxy()
    #tor_process = start_tor()
    set_dns()
    #return tor_process

#Set up proxy service
def set_proxy():
    socks.setdefaultproxy(socks.SOCKS5, PROXY_IP, SOCKS_PORT)
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
    return tor_process

def stop_tor(tor_process):
    tor_process.kill()

#Avoid DNS leaks by performing DNS resolution via the socket
def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

def set_dns():
    socket.getaddrinfo = getaddrinfo

#Permits identitty of scraping application to resemeble that of a browser
def create_user_agent():
    opener = urllib2.build_opener()
    #urllib2.HTTPSHandler(debuglevel=1), urllib2.HTTPHandler(debuglevel=1)
    opener.addheaders = [
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Encoding', 'gzip, deflate, sdch'),
            ('Accept-language', 'en-US,en;q=0.8'),
            ('Connection', 'keep-alive'),
            ('User-agent', global_const.USER_AGENT)
            ]
    urllib2.install_opener(opener)
    #anonymize()
