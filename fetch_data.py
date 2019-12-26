"""
    This script is created by https://github.com/amarder/diamonds/blob/master/download.py

"""
import re
import json
import time
import requests
import pandas as pd


def _price_to_int(s):
    return int(re.sub('[$,]', '', s))

class Diamonds:
    """
        Get Diamonds data from BlueNile API

        Currently only allows grab 1000 diamonds for each query.
        To get around this, use price to page thru results. ie.
        1. Get first 1000 diamonds
        2. Use diamond with highest price to seed the next query
    """
    HOME_URL = 'http://www.bluenile.com'
    API_URL = 'http://www.bluenile.com/api/public/diamond-search-grid/v2'

    def __init__(self):
        self.result = []
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

    def addParams(self, params={}):
        self.params.update(params)

    def download(self):
        landing_page = requests.get(self.HOME_URL)
        while True:
            try:
                response = requests.get(self.API_URL, self.params, cookies=landing_page.cookies)
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

            d = json.loads(response.text)
            for i in range(len(d['results'])):
                p = d['results'][i]['price']
                d['results'][i]['price'] = _price_to_int(p)
            max_price, min_price = d['results'][-1]['price'], d['results'][0]['price']

            last_page = params['pageSize'] >= d['countRaw']
            if last_page:
                self.result += d['results']
                break
            else:
                assert min_price < max_price, 'There are over {} diamonds with these characteristics at this price {} and up.' % (params['pageSize'], min_price)
                # only add diamonds with price lower than max
                self.result += [x for x in d['results'] if x['price'] < max_price]
                self.params['minPrice'] = max_price
        print("Complete: downloaded {} diamonds for given characteristics.".format(len(self.result)))

    def clean(self):
        # Put the data into a data frame.
        df = pd.DataFrame(self.result)

        # Clean up the data.
        for col in ['carat', 'depth', 'lxwRatio', 'table']:
            df[col] = df[col].map(lambda s: s.replace(',', '')).astype(float)
        for col in ['price', 'pricePerCarat']:
            df[col] = df[col].map(_price_to_int)
        print("Complete: cleaned diamonds data and convert to pandas DataFrame.")
        self.df = df

    def writeCSV(self, path):
        self.df.to_csv(path, index=False)
        print("Complete: write to {}.".format(path))

if __name__ == '__main__':
    # just a referrence for param options
    param_options = {
        'shape': [
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
        # ascending order (replace min with max)
        'minCut': ['Good', 'Very Good', 'Ideal', 'Signature Ideal'],
        'minColor': ['J', 'I', 'H', 'G', 'F', 'E', 'D'],
        'minClarity': ['SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF', 'FL'],
        'minPrice': 0, #int
        'minCarat': 50., #float
    }
    # here is what actually queried
    required_params = {
        'shape': 'RD'
    }

    diamonds = Diamonds()
    diamonds.addParams(required_params)
    diamonds.download()
    diamonds.clean()
    diamonds.writeCSV('./diamonds.csv')



