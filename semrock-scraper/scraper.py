# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 12:18:56 2018

@author: Doug
"""

import scrapy

class SemrockSpider(scrapy.Spider):
    name="semrock_spider"
    max_filters = 20
    #start_urls=['https://www.semrock.com/filters.aspx']
    start_urls=['https://www.semrock.com/filtersRefined.aspx?page=1&minWL=0&maxWL=2000&so=0&recs='+str(max_filters)]
    
    def parse(self, response):
        FILTER_SELECTOR='.partResultsItem'
        for filt in response.css(FILTER_SELECTOR):
            PART_SELECTOR = 'h1 a ::text'
            LINK_SELECTOR = 'h1 a ::attr(href)'
            yield{
                'name': filt.css(PART_SELECTOR).extract_first().strip(), 
                'link': filt.css(LINK_SELECTOR).extract_first().strip()
            } 
            
        NEXT_PAGE_SELECTOR = '.paging_link a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract()[-1]
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )