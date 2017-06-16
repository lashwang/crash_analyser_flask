#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import arrow


logger = logging.getLogger(__name__)



class ObjFinder(object):

    URL = 'http://10.10.10.22:8080/job/adclear_2_0/'
    URL_BASE = 'http://10.10.10.22:8080'

    def __init__(self,version_code = 0,index_file = "index.json"):
        self.version_code = version_code
        self.index = {}
        self.index_file = index_file


    def sync_from_server(self):
        try:
            r = requests.get(self.__class__.URL)
            self.parse_jenkins_main_page(r.content)
        except Exception,error:
            print error



    def parse_jenkins_main_page(self,content):
        html = BeautifulSoup(markup=content, features='lxml')

        all = html.find(id='buildHistory').find_all(class_="build-row no-wrap ")

        for item in all:
            url = item.find(class_="tip model-link inside").attrs['href']
            url = self.__class__.URL_BASE + url
            build_number = url.split('/')[-2]
            try:
                version_code = self.parse_version_code(url)
            except Exception:
                continue
            #print build_number,version_code
            self.index[build_number] = version_code

        print self.index


    def parse_version_code(self, url):
        r = requests.get(url)
        html = BeautifulSoup(markup=r.content, features='lxml')

        all_lines = html.find(class_="fileList").find_all('tr')

        if len(all_lines) != 5:
            raise ValueError

        apk_name = all_lines[0].find_all('td')[1].text
        version_code = apk_name.split('_')[4]
        version_code = version_code.replace('.','')

        return version_code

    def save_index_file(self):
        date = arrow.now().format('YYYY-MM-DD')
        raw_data = {}
        raw_data['update'] = date
        raw_data['index'] = self.index
        data = json.dumps(raw_data)
        with open(self.index_file, 'w') as outfile:
            json.dump(data, outfile)

    def load_index_file(self):
        with open(self.index_file) as data_file:
            data = json.loads(json.load(data_file))

        self.index_update_time = arrow.get(data['update'],'YYYY-MM-DD')
        self.index = data['index']
