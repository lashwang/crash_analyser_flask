#!/usr/bin/python
# -*- coding: utf-8 -*-

import fire
import commands
import os
import tarfile

brand_job_path = ''
next_build_number = 0

CACHE_FOLDER = 'caches'


def init(version,brand,lib,address):
    global brand_job_path
    global next_build_number
    global CACHE_FOLDER


    brand_job_path = '/jenkins_jobs/jobs/{}'.format(brand)
    next_build_number = int(
        commands.getstatusoutput('cat {}/nextBuildNumber'.format(brand_job_path,))[1])

    CACHE_FOLDER = 'caches_{}'.format(brand)


#find /jenkins_jobs/jobs/adclear_4_0/builds/226/archive/adclear/build/outputs/apk/ -name "*.apk"
def find_build_number_by_version(version):
    build_number_list = []
    for i in range(1, next_build_number):
        apk_path = '{}/builds/{}/archive/adclear/build/outputs/apk/'.format(brand_job_path,i)
        output = commands.getstatusoutput('find {} -name "*.apk"'.format(apk_path))
        code = output[0]
        if code == 0:
            if version in output[1]:
                build_number_list.append(i)
                print "find build number ({}) for {}".format(i,version)

    return build_number_list


def copy_lib_file_to_local(build_number_list):
    if not os.path.exists(CACHE_FOLDER):
        os.mkdir(CACHE_FOLDER)



    # /jenkins_jobs/jobs/adclear_4_0/builds/1/archive/adclear/build/outputs/proxy_objs.tar.bz2
    for build_number in build_number_list:
        local_build_path = os.path.join(CACHE_FOLDER, build_number)
        if not os.path.exists(local_build_path):
            os.mkdir(local_build_path)
        obj_path = '{}/builds/{}/archive/adclear/build/outputs/proxy_objs.tar.bz2'.format(brand_job_path,build_number)
        # extract proxy file
        with tarfile.open(obj_path, 'r:bz2') as tar:
            subdir_and_files = [
                tarinfo for tarinfo in tar.getmembers()
                if 'libproxy.so' in tarinfo.name
            ]
            tar.extractall(members=subdir_and_files,path=local_build_path)



def find_address(version='508594',brand='adclear_4_0',lib='proxy',address='0x1bfd44'):
    print "find_address for address={},version={},brand={},libname={}".format(address,version,brand,lib)
    init(version,brand,lib,address)
    build_number_list = find_build_number_by_version(version)
    copy_lib_file_to_local(build_number_list)
    pass

if __name__ == '__main__':
    fire.Fire(find_address)






