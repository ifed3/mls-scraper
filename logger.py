import logging

LOG_FILENAME = 'logfile.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

logging.debug('Log this message')
