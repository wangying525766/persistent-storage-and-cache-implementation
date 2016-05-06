import logging
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from xmlrpclib import Binary
import sys, pickle, xmlrpclib
#from pymongo import MongoClient
from pymongo import MongoClient
from bson.binary import Binary
import pickle
from datetime import datetime, timedelta
import time

conn = MongoClient('localhost:27017')
db = conn.test
#test = {"name":"imouren"}
key = "/a&&data"
now = datetime.now()
#value = {'st_ctime': 1445195690.610009, 'st_mtime': 1445195690.610009, 'st_nlink': 2, 'st_atime': 1445195690.610009, 'st_mode': 16877}
value = ""
Binary_value = pickle.dumps(value)
print "Binary_value:",Binary_value
db.test.insert({'key-data': Binary(key), 'value-data':Binary(Binary_value)})
tet=db.test.find()
for x in tet:
    print "VALUE IN DATABASE:    :", x


cursor = db.user1.find({'key-data': Binary(key)}).sort( [['_id', -1]] ).limit(1)

if (cursor!= None):
    for y in cursor:
        print "NOTE get getResult:", pickle.loads(Binary(y['value-data']))


'''
cursor = db.user1.find({'key-data': Binary(key)})
if (cursor!= None):
#print "NOTE get getResult:", pickle.loads(Binary(res['value-data'][0]))
    for res in cursor:
        print "NOTE get getResult:", pickle.loads(Binary(res['value-data'][0]))
else:
    print "hehe"  
'''
#db.foo.insert({'key-data': "1455", 'value-data':"345"})
#db.foo.save(test)
#cursor = db.foo.find({'key-data': "1455"})
#for i in cursor:
#	print i
