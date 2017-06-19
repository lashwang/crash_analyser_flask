import unittest
from obj_finder import ObjFinder
import tarfile


class MyTestCase(unittest.TestCase):
    def test_something(self):
        obj_finder = ObjFinder(version_code='700504862',index_file='test.json')
        #obj_finder.query_address('proxy','1189f8')
        obj_finder.parse_jenkins_local_file()

    @unittest.skip("skip")
    def testTarFile(self):
        with tarfile.open("test_file/proxy_objs.tar.bz2",'r:bz2') as tar:
            subdir_and_files = [
                tarinfo for tarinfo in tar.getmembers()
                if 'proxy/src/main/obj/local/armeabi/libproxy.so' == tarinfo.name
            ]
            tar.extractall(members=subdir_and_files)


if __name__ == '__main__':
    unittest.main()
