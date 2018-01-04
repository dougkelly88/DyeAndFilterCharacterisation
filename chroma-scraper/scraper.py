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
import os

class ChromaSpider(scrapy.Spider):
    name="chroma_spider"
    filters_per_page = 20
    start_urls=['https://www.chroma.com/products/single-bandpass-and-single-edge-filters', 
                'https://www.chroma.com/products/multi-bandpass-and-multi-dichroic-filters']
    
#    def __init__(self, category=None):
#        self.failed_filters = []
#        self.pn = ''
#        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
#        os.mkdir('Dichroic')
#        os.mkdir('Long pass')
#        os.mkdir('Short pass')
#        os.mkdir('Filter')
        
    
    def parse(self, response):
        FILTER_ROW_SELECTOR = '.pvm'
        for row in response.css(FILTER_ROW_SELECTOR):
            FILTER_NAME_SELECTOR = './/h2/a/text()'
            DETAILS_LINK_SELECTOR = './/h2/a/@href'
            yield{
                    'name': row.xpath(FILTER_NAME_SELECTOR).extract(), 
                    'link': row.xpath(DETAILS_LINK_SELECTOR).extract()
                    }
            
        NEXT_PAGE_SELECTOR = '//*[@id="pager-next-footer"]/a/@href'
        next_page = response.xpath(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

        
    
    def parse_details(self, response):
        DATA_LINK_SELECTOR = '//*[@id="tabs-detail_page_plot-left"]/div/div[1]/div/div/div/div/div[2]/div/table/tbody/tr/td[6]/span/a/@href'
        NAME_SELECTOR = 'body > div.wrapper > div > div.layout > div.body.clearfix > div > div.content > div > div > div > div.content-top > div > div > div > div > div.layout-plot-region.layout-plot-top > h2 > a ::text'
        yield {
            'filt name': response.css(NAME_SELECTOR).extract_first().strip(), 
            'lnk': response.xpath(DATA_LINK_SELECTOR).extract_first()
            }
            
            
#    def save_txt(self, response):
#               
#        path = response.url.split('/')[-1]
#        if (path[0:2]) == 'Di':
#            path = os.path.join('Dichroic', path)
#        elif (path[0:2]) == 'LP':
#            path = os.path.join('Long pass', path)
#        elif (path[0:2] == 'SP'):
#            path = os.path.join('Short pass', path)
#        else:
#            path = os.path.join('Filter', path)
#        
#        self.logger.info('Saving txt %s', path)
#        with open(path, 'wb') as f:
#            f.write(response.body)
            
    def handle_spider_closed(self, spider):
        self.logger.info('FINISHED!')
        self.logger.info('There were %d failed filters', len(self.failed_filters))
        self.logger.info('Failed at %s', ', '.join(self.failed_filters))
        with open('failures.csv', 'w') as f:
            f.write('\n'.join(self.failed_filters))
        
    def handle_errs(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.info('\n\nFAILURE!\n')
            self.logger.info('%s\n\n', response.url.split('/')[-1].replace('_Spectrum.txt', '\n'))            
            self.failed_filters.append(response.url.split('/')[-1].replace('_Spectrum.txt', ''))
    