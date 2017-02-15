'''
Connecting to site
'''
from config import *
from time import sleep
import requests
from MyAdapter import MyAdapter


def Connection():
    # Connecting to server
    count = 0
    while True:
        try:
            logging.info('Connecting to ' + URL)
            client = requests.session()
            client.mount('https://', MyAdapter())
            client.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
            # Retrieve the CSRF token first
            r1 = client.get(URL, timeout=(6.05, 27))
            csrftoken = r1.cookies['csrftoken']
            # Set login data and perform submit
            login_data = dict(username=USER, password=PASS, csrfmiddlewaretoken=csrftoken, next='/')
            try:
                r = client.post(URL, data=login_data, headers=dict(Referer=URL), timeout=6.05)
                page_source = 'Page Source for ' + URL + '\n' + r.text
            except Exception, e:
                logging.error('Some error during posting to ' + URL)
                logging.error(e)
            # logging.debug('Page Source for ' + URL + '\n' + r.text)
            # if Debugging is enabled Page source goes to debug.log file
            if Debugging == True:
                Store_Debug(page_source, "connection.log")
            return client
        except Exception, e:
            logging.error('Some error during connecting to ' + URL)
            logging.error(e)
            logging.error('Trying again after 60 seconds')
            count += 1
            if count > 5:
                logging.error('Performing delay for 1800 seconds')
                sleep(1800)
                count = 0
            sleep(60)
