#!/usr/bin/env python

import logging
import pickle, xmlrpclib
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
from xmlrpclib import Binary
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

def get_dict(a):
    server.read_file(Binary('./data_file'))
    output_g = server.get(Binary(a))
    #print output_g
    output_g = pickle.loads(output_g['value'].data)
    # print output_g
    return output_g

def put_dict(b,c):
    output_p = pickle.dumps(c)
    server.put(Binary(b),Binary(output_p),3000)

def write_file():
    server.write_file(Binary('./data_file'))

class Memory(LoggingMixIn, Operations):
  'Example memory filesystem. Supports only one level of files.'
  def __init__(self):
      print "init"
      # self.files = {}
      # self.data = defaultdict(bytes)
      put_dict("data1",defaultdict(bytes))
      put_dict("file",{})
      write_file()
  # get_dict("data1")
  # get_dict("file")
  # a= get_dict("data")
  # b= get_dict("file")
  # print a, b
  # output = pickle.dumps({})
  # server.put(Binary("data"),Binary(output),3000)
  # server.put(Binary("file"),Binary(output),3000)
  # server.print_content()
  # server.write_file(Binary('./data_file'))
  # a={'a':1}
  # put_dict("data",a)
  # server.write_file(Binary('./data_file'))
  # get_dict("data")
      self.fd = 0
      now = time()
      output_file = get_dict("file")
      output_file['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now,st_nlink=2)
      put_dict("file",output_file)
      write_file()
# self.files['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
# st_mtime=now, st_atime=now, st_nlink=2)

  def chmod(self, path, mode):
      print "chmod"
      output_file = get_dict("file")
      output_file[path]['st_mode'] &= 0770000
      output_file[path]['st_mode'] |= mode
      put_dict("file",output_file)
      write_file()
# self.files[path]['st_mode'] &= 0770000
# self.files[path]['st_mode'] |= mode
      return 0

  def chown(self, path, uid, gid):
      print "chown"
      output_file = get_dict("file")
      output_file[path]['st_uid'] = uid
      output_file[path]['st_gid'] = gid
      put_dict("file",output_file)
      write_file()
# self.files[path]['st_uid'] = uid
# self.files[path]['st_gid'] = gid

  def create(self, path, mode):
      print "create"
      output_file = get_dict("file")
      output_file[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,st_size=0, st_ctime=time(), st_mtime=time(),st_atime=time())
      put_dict("file",output_file)
      write_file()
# self.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
# st_size=0, st_ctime=time(), st_mtime=time(),
# st_atime=time())
      self.fd += 1
      return self.fd

  def getattr(self, path, fh=None):
      print "getattr"
      output_file = get_dict("file")
      if path not in output_file:
        raise FuseOSError(ENOENT)
# if path not in self.files:
# raise FuseOSError(ENOENT)
      return output_file[path] #self.files[path]

  def getxattr(self, path, name, position=0):
      print "getxattr"
      output_file = get_dict("file")
      attrs = output_file[path].get('attrs',{})
    #  print attrs,output_file[path]
      put_dict("file",output_file)
      write_file()
# attrs = self.files[path].get('attrs', {})
      try:
        return attrs[name]
      except KeyError:
        return '' # Should return ENOATTR
 
  def listxattr(self, path):
      print "listxattr"
      output_file = get_dict("file")
      attrs = output_file[path].get('attrs',{})
      print attrs,output_file[path]
      put_dict("file")
      write_file()
# attrs = self.files[path].get('attrs', {})
      return attrs.keys()

  def mkdir(self, path, mode):
      print "mkdir"
      output_file = get_dict("file")
      output_file[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2, st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time())
# self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
# st_size=0, st_ctime=time(), st_mtime=time(),
# st_atime=time())
      output_file['/']['st_nlink'] += 1
      put_dict("file",output_file)
      write_file()
# self.files['/']['st_nlink'] += 1 

  def open(self, path, flags):
      print "open"
      self.fd += 1
      return self.fd

  def read(self, path, size, offset, fh):
      print "read"
      output = get_dict("data1")
# output1 = output[path]
     # print output
    #  output = output[path]
    #  print output
      return output[path][offset:offset + size] #self.data[path][offset:offset + size]

  def readdir(self, path, fh):
      print "readdir"
      output_file = get_dict("file")
      return ['.', '..'] + [x[1:] for x in output_file if x != '/']
# return ['.', '..'] + [x[1:] for x in self.files if x != '/']

  def readlink(self, path):
      print "readlink"
      output = get_dict("data1")
      return output[path]#self.data[path]

  def removexattr(self, path, name):
      print "removexattr"
      output_file = get_dict("file")
      attrs = output_file[path].get('attrs',{})
     # attrs = self.files[path].get('attrs', {})
#put_dict("file")
#write_file()
      try:
        del attrs[name]
        put_dict("file")
        write_file()
      except KeyError:
        pass # Should return ENOATTR

  def rename(self, old, new):
      print "rename"
      output_file = get_dict("file")
      output_file[new] = output_file.pop(old)
# self.files[new] = self.files.pop(old)
      put_dict("file",output_file)
      write_file()

  def rmdir(self, path):
      print "rmdir"
      output_file = get_dict("file")
      output_file.pop(path)
      output_file['/']['st_nlink'] -= 1
      put_dict("file",output_file)
      write_file()
# self.files.pop(path)
# self.files['/']['st_nlink'] -= 1

  def setxattr(self, path, name, value, options, position=0):
      print "setxattr"
# Ignore options
      output_file = get_dict("file")
      attrs = output_file[path].setdefault('attrs', {})
      attrs[name] = value
# attrs = self.files[path].setdefault('attrs', {})
# attrs[name] = value

  def statfs(self, path):
      print "statfs"
      return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

  def symlink(self, target, source):
      print "symlink"
      output_file = get_dict("file")
      output_file[target] = dict(st_mode=(S_IFLNK | 0777), st_nlink=1, st_size=len(source))
# self.files[target] = dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
# st_size=len(source))
      output = get_dict("data1")
      output[target] = source
      put_dict("data1",output)
      put_dict("file",output_file)
      write_file()
# self.data[target] = source

  def truncate(self, path, length, fh=None):
      print "truncate"
      output = get_dict("data1")
      output[path] = output[path][:length]
      put_dict("data1",output)
# self.data[path] = self.data[path][:length]
      output_file = get_dict("file")
      output_file[path]['st_size'] = length
# self.files[path]['st_size'] = length
      put_dict("file",output_file)
      write_file()

  def unlink(self, path):
      print "unlink"
      output_file = get_dict("file")
      output_file.pop(path)
      put_dict("file",output_file)
      write_file()
# self.files.pop(path)

  def utimens(self, path, times=None):
      print "utimens"
      now = time()
      atime, mtime = times if times else (now, now)
      output_file = get_dict("file")
      output_file[path]['st_atime'] = atime
      output_file[path]['st_mtime'] = mtime
# self.files[path]['st_atime'] = atime
# self.files[path]['st_mtime'] = mtime
      put_dict("file",output_file)
      write_file()

  def write(self, path, data, offset, fh):
      print "write"
# self.data[path] = self.data[path][:offset] + data
      output = get_dict("data1")
      output_file = get_dict("file")
      if path not in output:
        output[path] = bytes()
      output[path] = output[path][:offset] + data
      output_file[path]['st_size'] = len(output[path])
# self.files[path]['st_size'] = len(output[path]) #(self.data[path])
      put_dict("data1",output)
      put_dict("file",output_file)
      write_file()
      return len(data)

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)
    server = xmlrpclib.ServerProxy('http://localhost:51234')
    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True)
