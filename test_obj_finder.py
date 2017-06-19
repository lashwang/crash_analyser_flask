import unittest
from obj_finder import ObjFinder
import tarfile


class MyTestCase(unittest.TestCase):
    @unittest.skip("skip")
    def test_something(self):
        obj_finder = ObjFinder(version_code='700504862',index_file='test.json')

    def testTarFile(self):
        with tarfile.open("test_file/proxy_objs.tar.bz2") as tar:
            subdir_and_files = [
                tarinfo for tarinfo in tar.getmembers()
                if tarinfo.name.contains('libproxy.so')
            ]
            tar.extractall(members=subdir_and_files)


if __name__ == '__main__':
    unittest.main()
