#!/usr/bin/env python
import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest
from datetime import datetime, timedelta
from xmlrpclib import Binary
import os
import logging
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
from time import time
import datetime
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from xmlrpclib import Binary
import sys, pickle, xmlrpclib
import threading
import time
import string
import commands
from datetime import datetime
import random
from collections import Counter



class SimpleHT:
  def __init__(self):
    self.data = {}
    self.next_check = datetime.now() + timedelta(minutes = 5)

  def count(self):
    # Remove expired entries
    self.next_check = datetime.now() - timedelta(minutes = 5)
    self.check()
    return len(self.data)
  
  # mediator send 
  def dataget(self, key):
    RandDataServer = random.sample(data_port_set, Qr)
    getBinaryResult = []
    getValResult = []
    print "--------------random select read dataserver-----------"
    print RandDataServer
    for e in RandDataServer:
      rpc = xmlrpclib.Server("http://localhost:%s" %e)
      tmp = rpc.get(key)
      getBinaryResult.append(tmp)
      if "value" in tmp:
        getValResult.append(pickle.loads(tmp["value"].data))
      else:
        getValResult.append('None')
      
      
    print  "--------------read value set-----------"
    print getBinaryResult
    print '---------get bi | get val--------'
    print getValResult
    #Find resluts that appeas most-commonly, choose this value as voter selected one
    countResult = Counter(getValResult)
    print countResult
    SelectValue = countResult.most_common()
    selectVal = SelectValue[0][0]
    indexNum = getValResult.index(selectVal)
    res = getBinaryResult[indexNum]
    print res
    return res
  
  # mediator send 
  def metaget(self, key):
    print "-------------metaget------------------"  
    rpc = xmlrpclib.Server("http://localhost:%s" %meta_port)
    res = rpc.get(key)
    return res
     
  # Insert something into the HT
  def dataput(self, key, value, ttl):
    if data_port_set == []:
      print "NO Data-Server Available For Write Request!"
      return False
    else:
      
      for PortNum in data_port_set:
          print "---------------------dataput send %s"  %PortNum
          rpc = xmlrpclib.Server("http://localhost:%s" %PortNum)
          rpc.put(key, value, 6000)
      print "-------------"
      print "simp put",(key.data,value.data,self.data)
      return True
    
  def metaput(self, key, value, ttl):
	
    rpc = xmlrpclib.Server("http://localhost:%s" %meta_port)
    print "-------------metaput------------------"
    rpc.put(key, value, 6000)
    print "simp put",(key.data,value.data,self.data)
    return True
    
  # Load contents from a file
  def read_file(self, filename):
    f = open(filename.data, "rb")
    self.data = pickle.load(f)
    f.close()
    return True

  # Write contents to a file
  def write_file(self, filename):
    f = open(filename.data, "wb")
    pickle.dump(self.data, f)
    f.close()
    return True

  # Print the contents of the hashtable
  def print_content(self):
    print self.data
    return True

  # Remove expired entries
  def check(self):
    now = datetime.now()
    if self.next_check > now:
      return
    self.next_check = datetime.now() + timedelta(minutes = 5)
    to_remove = []
    for key, value in self.data.items():
      if value[1] < now:
        to_remove.append(key)
    for key in to_remove:
      del self.data[key]
      
class Test(threading.Thread):
  
  def run(self):
      time.sleep(5)  
      self.runStatus = True
      while self.runStatus:
          portCheck=[]
          stat, proStr = commands.getstatusoutput("netstat -tpln")
          tmpStr = proStr
          tmpList = tmpStr.split("\n")
          del tmpList[0:4]
          for i in tmpList:
              val = i.split()
              if (val[-1].find('python') != -1):
                  result = val[3].split(":")
                  portCheck.append(result[1])         
          '''
          print "-------------"
          print portCheck
          print TotalPort
          print data_port_set
          print datetime.now()
          print "--------------"
          '''
          set_checked = set(portCheck)
          set_config = set(TotalPort)
          PortDiff = list(set_checked^set_config)
          #print PortDiff
          if PortDiff == []:
              time.sleep(3)
          else:
             
              fileopen = open ('run.sh','w')
              fileopen.seek(0)
              fileopen.truncate()
              for k in PortDiff:
                  if BackupPort == []:
                      print "-------------------NO SPARE PORT NUMBER AVAILABLE!------------------"
                      exit()					  
                  print k
                  command = "python simpleht_server.py "+BackupPort[0]+'&'
                  fileopen.write(command)
                  TotalPort.remove(k)
                  TotalPort.append(BackupPort[0])
                  data_port_set.remove(k)
                  data_port_set.append(BackupPort[0])
                  BackupPort.pop(0)  
              fileopen.close()
              os.system('bash run.sh')
              time.sleep(5)
    
  
          
          
  def stop (self):
      self.runStatus = False
      
      
# Start the xmlrpc server
def serve(port):
  file_server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', port))
  file_server.register_introspection_functions()
  sht = SimpleHT()
  file_server.register_function(sht.dataget)
  file_server.register_function(sht.dataput)
  file_server.register_function(sht.metaput)
  file_server.register_function(sht.metaget)
  file_server.register_function(sht.print_content)
  file_server.register_function(sht.read_file)
  file_server.register_function(sht.write_file)
  file_server.serve_forever()


def main():
  fileopen = open ('run.sh','w')
  fileopen.seek(0)
  fileopen.truncate()
  command = "python simpleht_server.py "+meta_port+'&'
  fileopen.write(command)
  for i in range(Qw):
    portNum = data_port_set[i] 
    command = "python simpleht_server.py "+portNum+'&'
    fileopen.write(command)
  fileopen.close()
  os.system('bash run.sh')

  port = 51234
  PortCheckThread = Test()
  PortCheckThread.start()
  serve(port)
  '''
  PortCheckThread = Test()
  PortCheckThread.start()
  time.sleep(12)
  PortCheckThread.stop()
  PortCheckThread.join()
  '''

		
if __name__ == "__main__":
  if len(argv) < 5:
    print 'usage: %s <Qr> <Qw> <meta_port> <data_port1>....<data_portN>' % argv[0]
    exit(1)
  if len(argv) != int(argv[2])  + 4:
    print 'usage: %s <Qr> <Qw> <meta_port> <data_port1>....<data_portN> where Qw should equal to data_portN' % argv[0]
    exit(1)
  global Qr
  Qr = int(argv[1])
  global Qw
  Qw = int(argv[2])
  global meta_port
  meta_port = argv[3]
  global data_port_set
  data_port_set = []
  for i in range(int(argv[2])):
    data_port_set.append(argv[4+i])
  global TotalPort
  TotalPort = list(data_port_set)
  TotalPort.append(meta_port)
  TotalPort.append("51234")
  print TotalPort
  print data_port_set
  global BackupPort 
  BackupPort = ['60000','60001','60002','60003','60004','60005','60006','60007','60008','60009','60010']
  main()
  
