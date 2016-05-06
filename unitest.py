#!/usr/bin/env python

import unittest
import os
import subprocess
from subprocess import check_output
import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest
from datetime import datetime, timedelta
from xmlrpclib import Binary
from sys import argv, exit
import os
import random
import commands
'''
Test-1
hierarchial directory creation--- fusemount/dir1/dir2/dir3
mkdir dir1;cddir dir1;mkdir dir2;chdir dir2;mkdir dir3;chdir dir3
list dir1, list dir2 check for correctness
Test-2
Creation of files in dir2 & dir3
create f21.txt,f22.txt & f31.txt,f32.txt
list dir2, list dir3 check for correctness
Test 3
Read files f21.txt , f22.txt
Test 4
Remove dir3
list dir2--check
Test 5- remove mile
rm f22.txt--list dir2 -- check
Test 6
mv dir2/f22.txt ../f11.txt
read dir1/f11.txt--check
'''

def writeIntoAFile(filename,string):
    f = open(filename,'w')
    f.write(string)
    f.close()
    
def readFile(filename):
    f = open(filename,'r')
    ret_string = f.read(3)
    f.close()
    return ret_string

basepath = '/home/ying/fusepy/project'

class FileSystemTest(unittest.TestCase):
           
    def test_01_NestedDirectories(self):
        os.chdir(basepath)
        os.chdir("fusemount")
        os.mkdir("dir1")
        os.chdir("dir1")
        os.mkdir("dir2")
        os.chdir("dir2")
        os.mkdir("dir3")
        os.chdir("dir3")
        path = os.path.join(basepath,'fusemount','dir1/dir2/dir3')
        self.assertEqual(os.getcwd(),path,"Nested directory creation failed")
        
    def test_02_NestedFileCreation(self):
        os.chdir(basepath)
        os.chdir("fusemount")
        os.chdir("dir1/dir2")
        writeIntoAFile("f21.txt","f21")
        writeIntoAFile("f22.txt","f22")
        contents1 = sorted(os.listdir("."))
        self.assertEqual(contents1,sorted(['dir3', 'f21.txt', 'f22.txt']),"Nested File creation failed")
        
    def test_03_ReadFiles(self):
        os.chdir(basepath)
        os.chdir("fusemount/dir1/dir2")
        ret_val = readFile("f22.txt")
        self.assertEqual(ret_val,"f22","Read test on files failed")
        
    def test_04_removeFile(self):
        os.chdir(basepath)
        os.chdir("fusemount/dir1/dir2/")
        os.remove("f22.txt")
        contents = sorted(os.listdir("."))
        self.assertEqual(contents,sorted(['dir3', 'f21.txt']),"File deletion failed")
        
    def test_05_removeDir(self):
        os.chdir(basepath)
        os.chdir("fusemount/dir1/dir2/")
        os.rmdir("dir3")
        contents = sorted(os.listdir("."))
        self.assertEqual(contents,sorted(['f21.txt']),"Directory deletion failed")
        
    def test_06_renameFile(self):
        os.chdir(basepath)
        os.chdir("fusemount/dir1/dir2/")
        os.rename("f21.txt","../../f11.txt")
        os.chdir("../..")
        contents = sorted(os.listdir("."))
        self.assertEqual(contents,sorted(['dir1', 'f11.txt']),"File renaming failed")
        
    def test_07_list_contents(self):
        print ''
        print "Now we will randomly select a server and print its content"
        stat, proStr = commands.getstatusoutput("netstat -tpln")
        portCheck=[]
        tmpStr = proStr
        tmpList = tmpStr.split("\n")
        del tmpList[0:4]
        for i in tmpList:
            val = i.split()
            if (val[-1].find('python') != -1):
                result = val[3].split(":")
                portCheck.append(result[1])
        RandDataServer = random.sample(portCheck[2:], 1)
        RandDataServer=''.join(RandDataServer)
        print ""
        print "We select %s port from the listened port set %s" %(RandDataServer,portCheck)
        rpc = xmlrpclib.Server("http://localhost:%s" %str(RandDataServer))
        contents=rpc.list_contents()
        print "The contents in port %s is shown as below" %RandDataServer
        print contents  
    
    def test_08_corrupt(self):
        print ''
        print "Now we will randomly select a data server, corrupt it content and then print the corrupt content with its original value"
        stat, proStr = commands.getstatusoutput("netstat -tpln")
        portCheck=[]
        tmpStr = proStr
        tmpList = tmpStr.split("\n")
        del tmpList[0:4]
        for i in tmpList:
            val = i.split()
            if (val[-1].find('python') != -1):
                result = val[3].split(":")
                portCheck.append(result[1])
        RandDataServer = random.sample(portCheck[2:], 1)
        RandDataServer=''.join(RandDataServer)
        print ""
        print "We select %s port from the listened port set %s" %(RandDataServer,portCheck)
        rpc = xmlrpclib.Server("http://localhost:%s" %str(RandDataServer))
        contents=rpc.corrupt('/&&data')
        print "The content before corrupt and after corrupt in port %s is shown as below" %RandDataServer
        print contents
        contents=rpc.list_contents()
        print 'Total content is shown'
        print contents

    def test_09_terminate(self):
        print ''
        print "Now we will randomly select a data server and terminate it to see the restart process"
        stat, proStr = commands.getstatusoutput("netstat -tpln")
        portCheck=[]
        tmpStr = proStr
        tmpList = tmpStr.split("\n")
        del tmpList[0:4]
        for i in tmpList:
            val = i.split()
            if (val[-1].find('python') != -1):
                result = val[3].split(":")
                portCheck.append(result[1])
        RandDataServer = random.sample(portCheck[2:], 1)
        RandDataServer=''.join(RandDataServer)
        print ""
        print "We select %s port from the listened port set %s to be terminated" %(RandDataServer,portCheck)
        rpc = xmlrpclib.Server("http://localhost:%s" %str(RandDataServer))
        if rpc.terminate():
      
            print "terminate port %s successfully" %str(RandDataServer)
            print "Now let's have a look at the exsiting port numbers"
            stat, proStr = commands.getstatusoutput("netstat -tpln")
            portCheck=[]
            tmpStr = proStr
            tmpList = tmpStr.split("\n")
            del tmpList[0:4]
            for i in tmpList:
                val = i.split()
                if (val[-1].find('python') != -1):
                    result = val[3].split(":")
                    portCheck.append(result[1])
            print portCheck
            print "After 3s the new server can be started. Port numbers is now as follows"
            time.sleep(3)
            stat, proStr = commands.getstatusoutput("netstat -tpln")
            portCheck=[]
            tmpStr = proStr
            tmpList = tmpStr.split("\n")
            del tmpList[0:4]
            for i in tmpList:
                val = i.split()
                if (val[-1].find('python') != -1):
                    result = val[3].split(":")
                    portCheck.append(result[1])
            print portCheck
        else:
            print "terminate error"
        
   
        
if __name__ == '__main__':
    unittest.main()
        
