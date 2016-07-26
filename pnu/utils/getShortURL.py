#! /usr/bin/env python3.5

import json
import requests

import logging
logging = logging.getLogger(__name__)

from pnu.config import private_config

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

        logging.info("Requesting shortened URL for: " + str(link))
        resp = requests.post(cls.POST_TO_URL, data=json.dumps(payload),
                headers=cls.HEADERS)
        logging.info("Got shortened URL: " + str(resp.json()))



if __name__ == "__main__":
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='../etc/logs/getShortURL.out',
            level=logging.DEBUG)

    logging.info("Beginning " + __file__)

    ShortenURL.get_short_url('http://google.com')


shortenURL = ShortenURL.get_short_url
