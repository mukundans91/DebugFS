from fuse import Fuse
import fuse
import os,stat,urllib,errno
import time

files=[]
dirs={'/':[]}
file_content={}
file_mode={}
dirpath=['/']
dir_mode={}


class MyStat(fuse.Stat):
	def __init__(self):
		self.st_mode=0
		self.st_nlink=0
		self.st_uid=0
		self.st_gid=0
		self.st_dev=0
		self.st_ino=0
		self.st_uid=0
		self.st_gid=0
		self.st_atime=0
		self.st_ctime=0
		self.st_mtime=0
		self.st_size=0

def Logger(fo,content):
	f=open("/home/mukundan/U1/FuseFS/log","a")
	f.write(fo+'<='+content+"\n")
	f.close()

class FuseFS(Fuse):
	test=[]
	def  getattr(self,path):#1
		st=MyStat()
		if path in dirpath:
			#st.st_mode=stat.S_IFDIR | 0777
			#st.st_nlink=2
			st=dir_mode[path]
		elif path in files:
			st=file_mode[path]
		else:
			return -errno.ENOENT
		return st
	def readdir(self,path,offset):#2
		global files,dirs
		tt=[l for l in files if path in l]
		#Logger('readdir before',str(tt))
		g=[]
		for l in tt:
			if '/' in l:
				l=l.rsplit('/',1)[1]
				g.append(l)
		tt=g
		for l in dirs[path]:
			l=l.rsplit('/',1)[1]
			tt.append(l)
		FuseFS.test.append(tt)
		#Logger('readdir after',str(tt))
		tt.append('.')
		tt.append('..')
		for r in tt:
			if r[0]!='.' and r[-1]!='~':
				yield fuse.Direntry(r)

	def rmdir(self,path):#3
		for l in files:
			if path in l:
				return
		dirpath.remove(path)
		dir_mode.pop(path)
		dirs.pop(path)
		folder,n=path.rsplit('/',1)
		if folder=='':
			folder='/'
		dirs[folder].remove(path)
		#Logger("rmdir",(str(dirs)))

	def chmod(self,path,mode):#4
		global file_mode,dir_mode
		if path in file_mode:
			st=file_mode[path]
			st.st_mode=stat.S_IFREG|mode
			file_mode[path]=st
			#Logger("chmod file",str(file_mode[path].st_mode))
		elif path in dir_mode:
			st=dir_mode[path]
			st.st_mode=stat.S_IFDIR|mode
			dir_mode[path]=st
			#Logger("chmod dir",str(dir_mode[path].st_mode))

	def mkdir(self,path,mode):#5
		folder,name=path.rsplit('/',1)
		if folder=='':
			folder='/'
		Logger("mkdir path",(str(path)))
		dirpath.append(path)
		dirs[folder].append(path)
		dirs[path]=[]
		st=MyStat()
		st.st_mode=stat.S_IFDIR|mode
		now=time.time()
		st.st_atime=now
		st.st_mtime=now
		st.st_ctime=now
		dir_mode[path]=st
		#Logger("mkdir",str(dirs)+"\n"+str(dirpath))

	def rename(self,old,new):#6
		if old in files:
			files.remove(old)
			files.append(new)
			c=file_content[old]
			file_content.pop(old)
			file_content[new]=c
			c=file_mode[old]
			file_mode.pop(old)
			file_mode[new]=c
			#Logger('rename',str(files)+"\n"+str(file_content)+"\n")
		elif old in dirpath:
			dirpath.remove(old)
			dirpath.append(new)
			folder,name=old.rsplit('/',1)
			if folder=='':
				folder='/'
			dirs[folder].remove(old)
			dirs[folder].append(new)
			c=dirs[old]
			dirs.pop(old)
			dirs[new]=c
			#Logger('rename dir',str(dirs)+"\n"+str(dirpath)+"\n")

	def mknod(self,path,mode,dev):#7
		global files,file_content,file_mode
		now=time.time()
		files.append(path)
		st=MyStat()
		st.st_mode=stat.S_IFREG | mode
		st.st_nlink=1
		st.st_ctime=now
		st.st_atime=now
		st.st_mtime=now
		file_mode[path]=st
		file_content[path]=''
		#Logger('mknod',str(files)+"\n"+str(file_content)+"\n")
		return 0

	def read(self, path, size, offset):#8
        	slen = len(file_content[path])
		if offset < slen:
		    buf = file_content[path][offset:offset+size]
		else:
		    buf = ''
		return buf

	def unlink(self,path):#9
		global files,file_content,file_mode
		files.remove(path)
		file_content.pop(path)
		file_mode.pop(path)
		#Logger('unlink',str(files)+"\n"+str(file_content)+"\n")

	def write(self,path,data,offset):#10
		global file_content,files,file_mode
		st=file_mode[path]
		c=file_content[path]
		newc=data
		file_content[path]=newc
		st.st_size=len(file_content[path])
		file_mode[path]=st
		#Logger('write',str(files)+"\n"+str(file_content)+"\n")
		return len(data)

	def truncate(self,path,length):#11
		if path in files:
			file_mode[path].st_size=length
		#Logger("truncate","path: "+path+" Size: "+length)

	
	def utimens(self,path,times=None):#12		#set time of append and modification
		try:
			now=time.time()
			now1=time.time()
			atime,mtime=(now,now1)
			st=file_mode[path]
			st.st_atime=atime
			st.st_mtime=mtime
			file_mode[path]=st
			return 0
			#Logger('utimens',str(st))
		except TypeError:
			return self.utime(path,times)

	def chown(self,path,uid,gid):#13		#Change ownership of directory
		global file_mode,dir_mode
		if path in file_mode:
			st=file_mode[path]
			st.st_uid=uid
			st.st_gid=gid
			file_mode[path]=st
			#Logger('chown file',str(st))
		elif path in dir_mode:
			st=dir_mode[path]
			st.st_uid=uid
			st.st_gid=gid
			dir_mode[path]=st
			#Logger('chown dir',str(st))


	def utime(self,path,times=None):#14		#set time of append and modification
		now=time.time()
		now1=time.time()
		atime,mtime=(now,now1)
		st=file_mode[path]
		st.st_atime=atime
		st.st_mtime=mtime
		file_mode[path]=st
		return 0
		#Logger('utime',str(st))

fuse.fuse_python_api=(0,2)

def createfile(name,content):
	global files,file_content,file_mode
	name='/'+name
	files.append(name)
	file_content[name]=content
	st=MyStat()
	st.st_mode=stat.S_IFREG|0777
	st.st_nlink=1
	st.st_size=len(file_content[name])
	file_mode[name]=st

def main():
	server=FuseFS(version="%prog "+fuse.__version__,usage="Error")
	server.parse(errex=1)
	server.main()

def initialize():
	server=FuseFS(version="%prog "+fuse.__version__,usage="Error")
	server.parse(errex=1)
	return server

if __name__=='__main__':
	main()
