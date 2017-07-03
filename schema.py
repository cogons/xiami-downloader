#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-06-16 19:05:49
# Project: xiami01

from pyspider.libs.base_handler import *
from pyspider.replay import h
import logging

import StringIO
import gzip

import re
import urllib
import urllib2
import json

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        url = 'http://www.xiami.com/artist/K1z4dbb3'
        self.crawl(url,callback=self.list_page)

    @config(age=2 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('div.info > p:nth-child(1) > strong > a').items():
            self.crawl(each.attr.href,callback=self.list_page)
     
       
    def list_page(self, response):
        for each in response.doc('#nav > a:nth-child(4)').items():
            self.crawl(each.attr.href,callback=self.sublist_page)
        for each in response.doc('#glory-nav > a:nth-child(5)').items():
            self.crawl(each.attr.href,callback=self.sublist_page) 
     
    def sublist_page(self, response):
        for each in response.doc('td.song_name > a:nth-child(1)').items():
            self.crawl(each.attr.href,callback=self.detail_page)
        
        for each in response.doc('#artist_hots > div.all_page > a.p_redirect_l').items():
            self.crawl(each.attr.href,callback=self.sublist_page)    

    
    @config(priority=2)
    def detail_page(self, response):
        try:
            def caesar(location):
                num = int(location[0])
                avg_len, remainder = int(len(location[1:]) / num), int(len(location[1:]) % num)
                result = [location[i * (avg_len + 1) + 1: (i + 1) * (avg_len + 1) + 1] for i in range(remainder)]
                result.extend([location[(avg_len + 1) * remainder:][i * avg_len + 1: (i + 1) * avg_len + 1] for i in range(num-remainder)])
                url = urllib.unquote(''.join([''.join([result[j][i] for j in range(num)]) for i in range(avg_len)]) + \
                             ''.join([result[r][-1] for r in range(remainder)])).replace('^','0')
                return url
        
            #get commot_count
            cmit=response.doc('#sidebar > div.music_counts > ul > li:nth-child(3) > a').text()
            cmit = cmit.encode('gbk')
            cmit=filter(str.isdigit,cmit)
        
            #get url for downloading
            try:
                num=response.doc('.do_collect .wrap').attr('onclick')
                num2=filter(str.isdigit,num)
                song_id=num2
                url = 'http://www.xiami.com/song/playlist/id/%s' % song_id + \
                '/object_name/default/object_id/0/cat/json'
                nresponse = h(url)
                secret = json.loads(nresponse)['data']['trackList'][0]['location']
                ourl = caesar(secret)
            except:
                ourl=""
                
           
            #get album img
            imgElem = response.doc("#albumCover > img")
            imgUrl = imgElem.attr.src
       
            return {
                "url": response.url,
                "title":response.doc('#title > h1').text(),
                "album":response.doc('tr:nth-child(1) > td:nth-child(2) > div > a').text(),
                "albun-img":imgUrl,
                "singer":response.doc('tr:nth-child(2) > td:nth-child(2) > div > a').text(),
                "songwritter":response.doc('tr:nth-child(3) > td:nth-child(2) > div').text(),
                "composer":response.doc('tr:nth-child(4) > td:nth-child(2) > div').text(),
                "lyrics":response.doc('#lrc > div.lrc_main').text(),
                "commit_count":cmit,           
                "tag":response.doc('#song_tags_block > div.content.clearfix').text(),
                "ourl":ourl
            }
        except:
            print('there is a mistake')
        


