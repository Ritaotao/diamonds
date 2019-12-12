"""
    This script is inspired by https://github.com/amarder/diamonds/blob/master/download.py

"""
import re
import json
import time
import requests

# just a referrence for param options
param_options = {
    'shapes': [
        "RD",  # round
        "PR",  # princess
        "EC",  # emerald
        "AS",  # asscher
        "CU",  # cushion
        "MQ",  # marquise
        "RA",  # radiant
        "OV",  # oval
        "PS",  # pear
        "HS",  # heart
    ],
    # ascending order
    'cuts': ['Good', 'Very Good', 'Ideal', 'Signature Ideal'],
    'colors': ['J', 'I', 'H', 'G', 'F', 'E', 'D'],
    'clarities': ['SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF', 'FL']
}


class diamonds:

    HOME_URL = 'http://www.bluenile.com'
    API_URL = 'http://www.bluenile.com/api/public/diamond-search-grid/v2'

    def __init__(self):
        self.df = None
        self.params = {
            'startIndex': 0,
            'pageSize': 1000,
            'country': 'USA',
            'language': 'en-us',
            'currency': 'USD',
            'sortColumn': 'price',
            'sortDirection': 'asc'
        }

    def parseParams(self, options):
        cuts = []


    def fetchData(self, params):
        landing_page = requests.get(self.HOME_URL)
        while True:
            try:
                response = requests.get(self.API_URL, params, cookies=landing_page.cookies)
            except:
                # if timeout
                time.sleep(60*30)
                next
            if not response.ok:
                # if server disconnected
                time.sleep(60*30)
            else:
                time.sleep(60*4)
                next

            result = json.loads(response.text)

