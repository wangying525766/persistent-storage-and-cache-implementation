#!/usr/bin/env python
"""
Author: David Wolinsky
Version: 0.02

Description:
The XmlRpc API for this library is:
  get(base64 key)
    Returns the value and ttl associated with the given key using a dictionary
      or an empty dictionary if there is no matching key
    Example usage:
      rv = rpc.get(Binary("key"))
      print rv => {"value": Binary, "ttl": 1000}
      print rv["value"].data => "value"
  put(base64 key, base64 value, int ttl)
    Inserts the key / value pair into the hashtable, using the same key will
      over-write existing values
    Example usage:  rpc.put(Binary("key"), Binary("value"), 1000)
  print_content()
    Print the contents of the HT
  read_file(string filename)
    Store the contents of the Hahelperable into a file
  write_file(string filename)
    Load the contents of the file into the Hahelperable
"""

import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest
from datetime import datetime, timedelta
from xmlrpclib import Binary
from sys import argv, exit
import os
import random
import threading

# Presents a HT interface
class SimpleHT:
  def __init__(self):
    self.data = {}
    self.next_check = datetime.now() + timedelta(minutes = 5)

  def count(self):
    # Remove expired entries
    self.next_check = datetime.now() - timedelta(minutes = 5)
    self.check()
    return len(self.data)

  # Retrieve something from the HT
  def get(self, key):
    # Remove expired entries
    self.check()
    # Default return value
    rv = {}
    # If the key is in the data structure, return properly formated results
    #print "simpleht_server GET key" ,(key)
    print "simpleht_server GET key"
    key = key.data
    #print "simpleht_server GET" ,(key,self.data)
    if key in self.data:
      ent = self.data[key]
      now = datetime.now()
      #print "simpleht_server GET ent", (ent,Binary(ent[0]))
      print "simpleht_server GET ent"
      if ent[1] > now:
        ttl = (ent[1] - now).seconds
        rv = {"value": Binary(ent[0]), "ttl": ttl}
      else:
        del self.data[key]
    return rv

  # Insert something into the HT
  def put(self, key, value, ttl):
    # Remove expired entries
    self.check()
    end = datetime.now() + timedelta(seconds = ttl)
    self.data[key.data] = (value.data, end)
    #print "simpleht_server put",(key.data,value.data,self.data)
    print "simpleht_server put"
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
  def list_contents(self):
    print "-----------------Key -> Data -------------------"
    #two solutions for search with different time cost, the other is 
    for key in self.data.keys(): 
      print "%s             --->              %s" %(key,self.data[key])
    return self.data

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
  
  def corrupt(self,key):
    key = Binary(key)  
    key = key.data
    if key in self.data:
      ent = self.data[key]
      corruptValue = str(random.randint(100, 1000000))
      tmplist = list(self.data[key])
      tmplist[0] = corruptValue
      self.data[key] = tuple(tmplist)          #since it is tuple element, we can't change it in common method
      returnValue = []
      returnValue.append(ent[0])
      returnValue.append(corruptValue)
      print self.data[key]
      print '------------data that is corruptted -> replace value----------'
      print returnValue   
      return returnValue
      
       
  def terminate(self):
    global killport
    killport = str(port)
    PortCheckThread = Test()
    PortCheckThread.start()
    return True

class Test(threading.Thread):
  def run(self): 
    time.sleep(0.3)      
    os.system('fuser -k  %s/tcp' %killport)

def main(portNum):
  global port
  port = int(portNum)
  serve(port)

# Start the xmlrpc server
def serve(port):
  file_server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', port))
  file_server.register_introspection_functions()
  sht = SimpleHT()
  file_server.register_function(sht.get)
  file_server.register_function(sht.put)
  file_server.register_function(sht.list_contents)
  file_server.register_function(sht.read_file)
  file_server.register_function(sht.write_file)
  file_server.register_function(sht.terminate)
  file_server.register_function(sht.corrupt)
  file_server.serve_forever()

if __name__ == "__main__":
  main(argv[1])

