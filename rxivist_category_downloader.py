'''
rxivist_category_downloader.py : download all metadata from Rxivist with specific category and 
a time range.
'''
from urllib import request
import numpy as np 
import time 
from collections import Counter

class RCategory:
    '''
    a class to fetch data from Rxivist and store into certain data structure

    Attrs:
    ----
    url:
    year:
    category:

    '''
    def __init__(self, mail, user, timeframe='alltime', category='neuroscience', num_pages=None, filename=None):
        self.timeframe = timeframe
        self.category  = category

        self.url = 'https://api.rxivist.org/v1/papers?category={}&timeframe={}'.format(
            self.category, self.timeframe)

        if filename:
            self.read_json(filename)

        else:
            self.first_page = request.urlopen(self.url)
            self.first_page = eval(self.first_page.read()) # turn to dict

            self.num_pages = self.first_page['query']['final_page']
            self.current_page = self.first_page['query']['current_page']

            # based on https://rxivist.org/docs
            self.header = {
                'User-Agent' : "{};mailto:{}".format(user, mail)
            }

            if num_pages:
                self.num_pages = num_pages

    def __repr__(self):
        return "the requested api url is {}; pages: {}; current_page: {}".format(
            self.url, self.num_pages, self.current_page)

    def fetch(self, sleep=10):
        '''
        fetch data with a certain Rxivist API, 
        page by page.
        '''
        self.results = self.first_page

        i = self.current_page + 1

        while self.current_page < self.num_pages:            
            self.current_page = i
            api = "{}&page={}".format(self.url, self.current_page)

            req = request.Request(api, headers=self.header)
            r = request.urlopen(req)

            try:
                print("[Info] requesting {}. ".format(
                    api), end="")

                cache = eval(r.read())

                self.results['results'] += cache['results']
                self.results['query']['current_page'] = self.current_page

                # sleep for a while to avoid exploiting the server
                time.sleep(sleep)

                i += 1            
                print("done.", end="\n")

            except NameError as e:
                print("You run too fast! Take a rest for 2 mins. {}".format(e))
                
                sleep += 1

                time.sleep(120)

    def n_grams(self, n):
        fullabs = " ".join([res['abstract'] for res in self.results['results']]) 

        # a brute force filter bag
        filter_bag = '''
        the of and in to a that we with is for by as this are on from these an were be was 
        or which our can using at during results but have both their data show it however across has 
        how also such been may used while when
        '''.replace('\n', '').split(' ')

        fullabs_bag = fullabs.lower().split(' ')
        fullabs_bag = [term for term in fullabs_bag if term not in filter_bag]

        count = Counter(zip(*[fullabs_bag[i:] for i in range(n)]))
        
        return count

    def read_json(self, filename):
        import json 

        with open(filename, "r") as f:
            self.results = json.load(f)

    def to_json(self):
        '''
        store dict to a json file
        '''
        import json

        with open("rxivist_{}.json".format(self.category), "w") as f:
            json.dump(self.results, f)

    @staticmethod
    def plot_bars(counts, n=20):
        '''
        plot the bar chart for most common words
        '''
        import altair as alt 
        import pandas as pd

        data = pd.DataFrame(
            counts.most_common(n), 
            columns=['category', 'count'])
        
        chart = alt.Chart(data).mark_bar().encode(
            x='count',
            y=alt.Y(
                'category', 
                sort=alt.SortField(field='freq', order='ascending')
            )
        )

        return chart