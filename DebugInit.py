import inspect
import DebugFS
import os

def functionInfo(func,level):
	funcInfo=''
	f=inspect.getargspec(func)
	funcInfo += '\t'*level+"Argument List : "+str(f[0])+"\n"
	funcInfo += '\t'*level+"Variable Argument List : "+str(f[1])+"\n"
	funcInfo += '\t'*level+"Keyword Argument List : "+str(f[2])+"\n"
	funcInfo += '\t'*level+"Default Values List : "+str(f[3])+"\n"
	return funcInfo

def inspectPreviousFrames():
	frame=inspect.currentframe()
	framesinfo=inspect.getouterframes(frame)
	framesInfo=[]
	for frames in framesinfo:
		frameInfo=''
		frame=frames[0]
		Glo=frame.f_globals
		if Glo['__name__']!=__name__:
			frameInfo+='Package Name : '+str(Glo['__package__'])+"\n"
			frameInfo+='File Name : '+str(Glo['__file__'])+"\n"
			frameInfo+='Module DocString : '+str(Glo['__doc__'])+"\n"
			frameInfo+='Module NameSpace : '+str(Glo['__name__'])+'\n'
			variables=[]
			functions=[]
			classes=[]
			modules=[]
			builtins=[]
			for f in Glo:
				if f not in ['__builtins__','__package__','__file__','__doc__','__name__']:
					if inspect.isfunction(Glo[f]):
						funcInfo=''
						funcInfo+=str(f)+" : "+str(Glo[f])+"\n"+functionInfo(Glo[f],level=1)+"\n"
						functions.append(funcInfo)
					elif inspect.isclass(Glo[f]):
						classInfo=''
						classInfo+=str(f)+" : "+str(Glo[f])+"\n"
						classes.append(classInfo)
					elif inspect.ismodule(Glo[f]):
						moduleInfo=''
						moduleInfo+=str(f)+" : "+str(Glo[f])+"\n"
						modules.append(moduleInfo)
					elif inspect.isbuiltin(Glo[f]):
						builtinInfo=''
						builtinInfo+=str(f)+" : "+str(Glo[f])+"\n"
						builtins.append(builtinInfo)
					else:
						variables.append(str(f)+" : "+str(Glo[f])+"\n")

			variables=sorted(variables)
			classes=sorted(classes)
			functions=sorted(functions)
			modules=sorted(modules)
			builtins=sorted(builtins)

			frameInfo+="List of Variables : \n"
			if variables:
				for c in variables:
					frameInfo+=c+"\n"
			else:
				frameInfo+="None\n"
			frameInfo+="List of Functions : \n"
			if functions:
				for c in functions:
					frameInfo+=c+"\n"
			else:
				frameInfo+="None\n"
			frameInfo+="List of Classes : \n"
			if classes:
				for c in classes:
					frameInfo+=c+"\n"
			else:
				frameInfo+="None\n"
			frameInfo+="List of Modules : \n"
			if modules:
				for c in modules:
					frameInfo+=c+"\n"
			else:
				frameInfo+="None\n"
			frameInfo+="List of Builtins : \n"
			if builtins:
				for c in builtins:
					frameInfo+=c+"\n"
			else:
				frameInfo+="None\n"
			framesInfo.append(frameInfo)
	finalFrameInfo=''
	for framesInfor in framesInfo:
		finalFrameInfo+=framesInfor
	return finalFrameInfo


class DInit:
	def __init__(self,argv):
		self.mountpoint=os.path.abspath(argv)

	def initialize(self):
		os.system('python DebugFS.py "'+self.mountpoint+'"')

	def writeCurrentState(self):
		self.filename='currentState.frInfo'
		if self.mountpoint[-1]!='/':
			self.absfilename=self.mountpoint+'/'+self.filename
		else:
			self.absfilename=self.mountpoint+self.filename
		self.currentStateFrameInfo=inspectPreviousFrames()
		fhandle=open(self.absfilename,"w")
		fhandle.write(self.currentStateFrameInfo)
		fhandle.close()

	def closeVFS():
		os.system("fusermount -u "+self.mountpoint)
