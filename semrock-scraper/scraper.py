# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 12:18:56 2018

@author: Doug

Usage: from base directory, type: scrapy runspider scraper.py
"""

import scrapy
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.spidermiddlewares.httperror import HttpError

class SemrockSpider(scrapy.Spider):
    name="semrock_spider"
    filters_per_page = 50
    #start_urls=['https://www.semrock.com/filters.aspx']
    start_urls=['https://www.semrock.com/filtersRefined.aspx?page=1&minWL=0&maxWL=2000&so=0&recs='+str(filters_per_page)]
    
    def __init__(self, category=None):
        self.failed_filters = []
        self.pn = ''
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
        
    
    def parse(self, response):
        FILTER_SELECTOR='.partResultsItem'
        for filt in response.css(FILTER_SELECTOR):
            PART_SELECTOR = 'h1 a ::text'
            self.pn = filt.css(PART_SELECTOR).extract_first().strip()
            self.logger.info('PN = %s', self.pn)
            old_url='https://www.semrock.com/_ProductData/Spectra/' + self.pn.replace('/', '_')
            dummy = old_url.rsplit('-', 1)
            new_url = dummy[0] + '_Spectrum.txt'

            yield Request(
                url = new_url, 
                callback=self.save_txt, 
                errback=self.handle_errs
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
            
    def handle_spider_closed(self, spider):
        self.logger.info('FINISHED!')
        self.logger.info('There were %d failed filters', len(self.failed_filters))
        self.logger.info('Failed at %s', ', '.join(self.failed_filters))
        with open('failures.csv', 'w') as f:
            f.write('\n'.join(self.failed_filters))
        
    def handle_errs(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.info('\n\nFAILURE!\n')
            self.logger.info('%s\n\n', response.url.split('/')[-1].replace('_Spectrum.txt', '\n'))            
            self.failed_filters.append(response.url.split('/')[-1].replace('_Spectrum.txt', ''))
    