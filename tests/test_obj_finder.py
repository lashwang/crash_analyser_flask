import unittest2
from obj_finder import ObjFinder



class MyTestCase(unittest2.TestCase):
    def test_something(self):
        obj_finder = ObjFinder(version_code='700504862',index_file='test.json')


if __name__ == '__main__':
    unittest2.main()
