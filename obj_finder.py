#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import requests
from bs4 import BeautifulSoup
import json
import arrow
import os
import os.path

import urllib
import time
import tarfile
import subprocess
import commands

logger = logging.getLogger(__name__)



class ObjFinder(object):

    '''
    http://10.10.10.22:8080/job/adclear_2_0/lastSuccessfulBuild/artifact/adclear/build/outputs/engine_objs.tar.bz2
    http://10.10.10.22:8080/job/adclear_2_0/lastSuccessfulBuild/artifact/adclear/build/outputs/proxy_objs.tar.bz2
    '''


    URL = 'http://10.10.10.22:8080/job/adclear_2_0/'
    URL_BASE = 'http://10.10.10.22:8080'

    CACHE_FOLDER = 'caches'

    OBJ_URL_FORMAT = 'http://10.10.10.22:8080/job/adclear_2_0/{}/artifact/adclear/build/outputs/{}'

    ENGINE_OBJ_NAMES = 'engine_objs.tar.bz2'
    PROXY_OBJ_NAMES = 'proxy_objs.tar.bz2'

    OBJ_PATH_FORMAT = '/jenkins_jobs/jobs/adclear_2_0/builds/{}/archive/adclear/build/outputs/'


    def __init__(self,version_code = 0,index_file = "index.json"):
        self.version_code = int(version_code)
        self.index = {}
        self.index_file = index_file
        self.sync_from_server()
        try:
            os.mkdir(self.__class__.CACHE_FOLDER)
        except Exception,error:
            print error

        print self.index

        self.find_build_numbers()
        self.sync_objects_files()


    def sync_from_server(self):
        try:
            self.load_index_file()

            if not self.is_index_file_out_date():
                return
        except Exception,error:
            print error

        try:
            r = requests.get(self.__class__.URL)
            self.parse_jenkins_main_page(r.content)
            self.save_index_file()
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
            self.index[build_number] = int(version_code)

    def parse_jenkins_local_file(self):
        next_build_number = int(commands.getstatusoutput('cat /jenkins_jobs/jobs/adclear_2_0/nextBuildNumber')[1])
        apk_path_format = '/jenkins_jobs/jobs/adclear_2_0/builds/{}/archive/adclear/build/outputs/apk/'
        for i in range(next_build_number-200,next_build_number):
            output = commands.getstatusoutput('ls {}'.format(apk_path_format.format(i)))
            code = output[0]
            if code == 0:
                apk_file_name = output[1].split('\n')[0]
                print i
                print apk_file_name





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



    def is_index_file_out_date(self):
        now = arrow.now().format('YYYY-MM-DD')
        old_time = (self.index_update_time).replace(days=+1).format('YYYY-MM-DD')

        if now >= old_time:
            return True

        return False



    def find_build_numbers(self):
        self.build_number_list = []

        for k,v in self.index.iteritems():
            if v == self.version_code:
                self.build_number_list.append(k)

    def dlProgress(self,count, blockSize, totalSize):
        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size = int(count * blockSize)
        speed = int(progress_size / (1024 * duration))
        percent = int(count * blockSize * 100 / totalSize)
        print("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                         (percent, progress_size / (1024 * 1024), speed, duration))


    def sync_objects_files(self):
        class_ = self.__class__
        for index in self.build_number_list:
            if self.check_lib_file_exist(index):
                print 'lib files for {} exist'.format(index)
                continue

            local_build_path = os.path.join(class_.CACHE_FOLDER,index)
            obj_path = class_.OBJ_PATH_FORMAT.format(index)
            engine_obj_path = os.path.join(obj_path,class_.ENGINE_OBJ_NAMES)
            proxy_obj_path = os.path.join(obj_path, class_.PROXY_OBJ_NAMES)

            #print engine_obj_path,proxy_obj_path

            if not (os.path.exists(engine_obj_path) or os.path.exists(proxy_obj_path)):
                raise ValueError

            # extract engine file
            with tarfile.open(engine_obj_path, 'r:bz2') as tar:
                subdir_and_files = [
                    tarinfo for tarinfo in tar.getmembers()
                    if 'liboc_engine.so' in tarinfo.name
                ]
                tar.extractall(members=subdir_and_files,path=local_build_path)
            engine_so_path = os.path.join(local_build_path,'engine/src/main/obj/local/armeabi/liboc_engine.so')
            os.system('ln -s {} {}'.format(engine_so_path,os.path.join(local_build_path,'liboc_engine.so')))

            # extract proxy file
            with tarfile.open(proxy_obj_path, 'r:bz2') as tar:
                subdir_and_files = [
                    tarinfo for tarinfo in tar.getmembers()
                    if 'libproxy.so' in tarinfo.name
                ]
                tar.extractall(members=subdir_and_files,path=local_build_path)

            proxy_so_path = os.path.join(local_build_path,'proxy/src/main/obj/local/armeabi/libproxy.so')
            os.system('ln -s {} {}'.format(proxy_so_path,os.path.join(local_build_path,'libproxy.so')))


    def check_lib_file_exist(self,build_number):
        class_ = self.__class__
        local_build_path = os.path.join(class_.CACHE_FOLDER, build_number)

        lib_engine_path = os.path.join(local_build_path,'liboc_engine.so')
        lib_proxy_path = os.path.join(local_build_path,'libproxy.so')

        #print os.path.lexists(lib_engine_path),lib_engine_path
        #print os.path.lexists(lib_proxy_path),lib_proxy_path

        return (os.path.lexists(lib_engine_path) and os.path.lexists(lib_proxy_path))


    def get_engine_so_full_path(self,build_number,type):
        class_ = self.__class__
        local_build_path = os.path.join(class_.CACHE_FOLDER, build_number)
        if type == 'proxy':
            return os.path.join(local_build_path,'proxy/src/main/obj/local/armeabi/libproxy.so')
        elif type == 'engine':
            return os.path.join(local_build_path,'engine/src/main/obj/local/armeabi/liboc_engine.so')


        raise ValueError(type)


    def query_address(self,type,address_list):
        query_result = {}
        for build_number in self.build_number_list:
            so_path = self.get_engine_so_full_path(build_number,type)
            cmd_result = commands.getstatusoutput('./addr2line_android -f -e {} {}'.format(so_path,address_list))
            print build_number
            print cmd_result
            query_result[build_number] = cmd_result[1]


        return query_result




