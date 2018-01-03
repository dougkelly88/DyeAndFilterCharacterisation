# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 12:18:56 2018

@author: Doug
"""

import scrapy
from scrapy.http import Request

class SemrockSpider(scrapy.Spider):
    name="semrock_spider"
    filters_per_page = 20
    #start_urls=['https://www.semrock.com/filters.aspx']
    start_urls=['https://www.semrock.com/filtersRefined.aspx?page=1&minWL=0&maxWL=2000&so=0&recs='+str(filters_per_page)]
    
    def parse(self, response):
        FILTER_SELECTOR='.partResultsItem'
        for filt in response.css(FILTER_SELECTOR):
            PART_SELECTOR = 'h1 a ::text'
            pn = filt.css(PART_SELECTOR).extract_first().strip()
            self.logger.info('PN = %s', pn)
            old_url='https://www.semrock.com/_ProductData/Spectra/' + pn.replace('/', '_')
            dummy = old_url.rsplit('-', 1)
            new_url = dummy[0] + '_Spectrum.txt'

            yield Request(
                url = new_url, 
                callback=self.save_txt
            )
            
#        NEXT_PAGE_SELECTOR = '.paging_link a ::attr(href)'
#        next_page = response.css(NEXT_PAGE_SELECTOR).extract()[-1]
#        if next_page:
#            yield scrapy.Request(
#                response.urljoin(next_page),
#                callback=self.parse
#            )
            
    def save_txt(self, response):
        path = response.url.split('/')[-1]
        self.logger.info('Saving txt %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)
    