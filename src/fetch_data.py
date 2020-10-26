"""
    This script is created by https://github.com/amarder/diamonds/blob/master/download.py

"""
import os, re, time
import glob
import json
import requests
import pandas as pd
from datetime import datetime

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
    'shape': 'RD',
    'minPrice': 10000,
    'maxPrice': 30000
}


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
        self.complete = False
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
        # may run into sslerror issue in this step, in case that happens, 
        # reinstall requests package with a different version
        landing_page = requests.get(self.HOME_URL)
        i = 0
        while True:
            try:
                response = requests.get(self.API_URL, self.params, cookies=landing_page.cookies)
            except:
                # if timeout
                time.sleep(30)
                next
            if not response.ok:
                # if server disconnected
                time.sleep(30)
            else:
                time.sleep(15)
                next

            try:
                d = json.loads(response.text)
                # new: return data all wrapped in a list - so always extract first element
                min_price = _price_to_int(d['results'][0]['price'][0])
                max_price = _price_to_int(d['results'][-1]['price'][0])
            except Exception as e:
                print(response.text)
                print(e)
                next

            last_page = self.params['pageSize'] >= d['countRaw']
            print("Number of remaining: {}".format(d['countRaw']))
            if last_page:
                self.result += d['results']
                break
            else:
                assert min_price < max_price, 'Min price bigger than max price'
                # only add diamonds with price lower than max
                self.result += [x for x in d['results'] if _price_to_int(x['price'][0]) < max_price]
                self.params['minPrice'] = max_price
                i += 1
                print("Iter {}: added {} diamonds".format(i, len(self.result)))
        print("Complete: downloaded {} diamonds for given characteristics.".format(len(self.result)))

    def clean(self):
        # Put the data into a data frame.
        df = pd.DataFrame(self.result)
        df = df.applymap(lambda x: x[0] if isinstance(x, list) else x)

        # Clean up the data.
        for col in ['carat', 'depth', 'lxwRatio', 'table']:
            df[col] = df[col].map(lambda s: s.replace(',', '')).astype(float)
        for col in ['price', 'pricePerCarat']:
            df[col] = df[col].map(_price_to_int)
        for col in ['cut', 'measurements']:
            df[col] = df[col].map(lambda s: s['label'])
        print("Complete: cleaned diamonds data and convert to pandas DataFrame.")
        self.df = df
        self.complete = True

    def writeCSV(self, path):
        self.df.to_csv(path, index=False)
        print("Complete: write to {}.".format(path))


def update_data(data_dir):
    """
        Download Diamonds data and clean historical data
        In case update failed, use the last existing csv file
        Return: 
            1) (string) new data file path
            2) (string): download status
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    current_date = datetime.today().strftime('%Y%m%d')
    output_path = os.path.join(data_dir, 'diamonds_{}.csv'.format(current_date))
    resp = ''
    if os.path.exists(output_path):
        resp = 'Diamonds data is already the latest copy: {}.'.format(current_date)
    else:
        # download diamonds data set
        diamonds = Diamonds()
        diamonds.addParams(required_params)
        diamonds.download()
        diamonds.clean()
        oldfile_list = glob.glob(os.path.join(data_dir, "*.csv"))
        if diamonds.complete:
            # remove older data files
            for f in oldfile_list:
                os.remove(f)
            diamonds.writeCSV(output_path)
            resp = 'Diamond data is updated to: {}.'.format(current_date)
        else:
            output_path = oldfile_list[-1]
            resp = 'Dimond data download for {} failed, use {} by default.'.format(current_date, output_path)
    print(resp)
    return output_path, resp

