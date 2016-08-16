#! /usr/bin/env python3.5

import json
import requests
import time

from pnu.config import private_config

import logging
logging = logging.getLogger(__name__)


class ShortenURL:

    POST_TO_URL = ("https://www.googleapis.com/urlshortener/v1/url?" +
            "fields=status%2Cid&key=" + private_config['goo.gl']['API_KEY'])
    HEADERS = {
            'content-type': 'application/json'
    }

    @classmethod
    def get_short_url(cls, link):
        payload = {
            'longUrl': link
        }

        logging.info("Requesting shortened URL for: {}".format(link))

        for i in range(5):
            resp = requests.post(cls.POST_TO_URL, data=json.dumps(payload),
                                 headers=cls.HEADERS)
            if resp.status_code == 200:
                # in case this is the 3rd try, we don't want to trip our
                # exception below
                i = 0
                break
            else:
                time.sleep(3)
                logging.warning("Google URL API status code is {}. Trying " +
                                "again...".format(resp.status_code))

        if i == 4:
            logging.error("Could not connect to Google URL API")
            return link

        logging.info("Got shortened URL: {}".format(resp.json()))

        return resp.json()['id']


if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/google_url_api.out',
            level=logging.DEBUG)

    logging.info("Beginning " + __file__)

    ShortenURL.get_short_url('http://google.com')


PnuUrlShortener = ShortenURL.get_short_url
