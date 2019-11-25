def folderWalk(folderPath):
	import os
	fileList = []
	for dirPath , dirNames , fileNames in os.walk(folderPath) :
		for fileName in fileNames :
			fileList.append(os.path.join(dirPath , fileName))
	return fileList
def fileListToFileNameDict(l):
	dic={}
	num=0
	for i in l:
		dic[num]=i
		num+=1
	return dic
