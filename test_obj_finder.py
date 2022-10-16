import unittest
from obj_finder import ObjFinder
import tarfile


test_stack_logs = '''
07-09 16:04:56.011  2419  2486 E [Native]OCEngine: 07-09 16:04:56.015 +0100 2486 [E] [oc_backtrace.cpp:76] (-2) - dumpping backtrace for client:700505113
07-09 16:04:56.021  2419  2486 E [Native]OCEngine: 07-09 16:04:56.027 +0100 2486 [E] [oc_backtrace.cpp:45] (-2) - dumpBacktrace,number:18
07-09 16:04:56.031  2419  2486 E [Native]OCEngine: 07-09 16:04:56.034 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 0: /data/app/com.seven.adclear-2/lib/arm/liboc_engine.so  0x654be2  0x9d4f0be2  log_backtrace
07-09 16:04:56.031  2419  2486 E [Native]OCEngine: 07-09 16:04:56.035 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 1: /data/app/com.seven.adclear-2/lib/arm/liboc_engine.so  0x654608  0x9d4f0608  
07-09 16:04:56.031  2419  2486 E [Native]OCEngine: 07-09 16:04:56.040 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 2: /system/lib/libart.so  0x35f374  0xb3e44374  art::FaultManager::HandleFault(int, siginfo*, void*)
07-09 16:04:56.031  2419  2486 E [Native]OCEngine: 07-09 16:04:56.040 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 3: /system/lib/libc.so  0x175cc  0xb6d225cc  
07-09 16:04:56.031  2419  2486 E [Native]OCEngine: 07-09 16:04:56.040 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 4: /data/app/com.seven.adclear-2/lib/arm/liboc_engine.so  0x439528  0x9d2d5528  ocengine::OCEngineTask::~OCEngineTask()
07-09 16:04:56.041  2419  2486 E [Native]OCEngine: 07-09 16:04:56.041 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 5: /data/app/com.seven.adclear-2/lib/arm/liboc_engine.so  0x586164  0x9d422164  ocengine::OCEngineTaskDnsCSQ::~OCEngineTaskDnsCSQ()
07-09 16:04:56.041  2419  2486 E [Native]OCEngine: 07-09 16:04:56.042 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 6: /data/app/com.seven.adclear-2/lib/arm/liboc_engine.so  0x57c252  0x9d418252  ocengine::ThreadPool::TaskLauncher::~TaskLauncher()
07-09 16:04:56.041  2419  2486 E [Native]OCEngine: 07-09 16:04:56.042 +0100 2486 [E] [oc_backtrace.cpp:65] (-2) - backtrace:  # 7: /data/app/com.seven.adclear-2/lib/arm/liboc_engine.so  0x57c83a  0x9d41883a  boost::detail::sp_counted_impl_p<ocengine::ThreadPool::TaskLauncher>::dispose()
'''



class MyTestCase(unittest.TestCase):

    @unittest.skip("skip")
    def test_something(self):
        obj_finder = ObjFinder(version_code='700504862',index_file='test.json')
        obj_finder.query_address('proxy','1189f8')
        #obj_finder.parse_jenkins_local_file()

    @unittest.skip("skip")
    def testTarFile(self):
        with tarfile.open("test_file/proxy_objs.tar.bz2",'r:bz2') as tar:
            subdir_and_files = [
                tarinfo for tarinfo in tar.getmembers()
                if 'proxy/src/main/obj/local/armeabi/libproxy.so' == tarinfo.name
            ]
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, members=subdir_and_files)

    def test_full_stack_logs(self):
        ObjFinder.query_full_stack_logs(test_stack_logs)


if __name__ == '__main__':
    unittest.main()
