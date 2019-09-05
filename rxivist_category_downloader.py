'''
rxivist_category_downloader.py : download all metadata from Rxivist with specific category and 
a time range.
'''
from urllib import request
import numpy as np 
import time 

class RCategory:
    '''
    a class to fetch data from Rxivist and store into certain data structure

    Attrs:
    ----
    url:
    year:
    category:

    '''
    def __init__(self, timeframe='alltime', category='neuroscience', num_pages=None):
        self.timeframe = timeframe
        self.category  = category

        self.url = 'https://api.rxivist.org/v1/papers?category={}&timeframe={}'.format(
            self.category, self.timeframe)

        self.first_page = request.urlopen(self.url)
        self.first_page = eval(self.first_page.read()) # turn to dict

        self.num_pages = self.first_page['query']['final_page']
        self.current_page = self.first_page['query']['current_page']

        if num_pages:
            self.num_pages = num_pages

    def __repr__(self):
        return "the requested api url is {}; pages: {}; current_page: {}".format(
            self.url, self.num_pages, self.current_page)

    def fetch(self, sleep=2):
        '''
        fetch data with a certain Rxivist API, 
        page by page.
        '''
        results = self.first_page

        # i=0 has already run
        for i in range(1, self.num_pages + 1):
            
            print("[Info] requesting {} w page {}.".format(
                self.url, self.current_page
            ), end="")

            self.current_page = i

            r = request.urlopen(
                "{}&page={}".format(self.url, self.current_page)
            )
            cache = eval(r.read())

            results['results'] += cache['results']
            results['query']['current_page'] = self.current_page

            # sleep for a while to avoid exploiting the server
            time.sleep(sleep)

            print("done.", end="\n")

        self.results = results

    def to_json(self):
        '''
        store dict to a json file
        '''
        import json

        with open("rxivist_{}.json".format(self.category), "w") as f:
            json.dump(self.results, f)
