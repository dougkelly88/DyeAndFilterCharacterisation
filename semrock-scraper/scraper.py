# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 12:18:56 2018

@author: Doug
"""

import scrapy

class SemrockSpider(scrapy.Spider):
    name="semrock_spider"
    max_filters = 2000
    #start_urls=['https://www.semrock.com/filters.aspx']
    start_urls=['https://www.semrock.com/filtersRefined.aspx?page=1&minWL=0&maxWL=2000&so=0&recs='+str(max_filters)]
    
    def parse(self, response):
        FILTER_SELECTOR='.partResultsItem'
        for filt in response.css(FILTER_SELECTOR):
            NAME_SELECTOR = 'h1 a ::text'
            yield{
                'name': filt.css(NAME_SELECTOR).extract_first().strip(), 
            } 