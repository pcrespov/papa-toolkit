'''
Borra directorios sin fotos
'''
from send2trash import send2trash
import os

def delemptydirs(top_path):
	del_dirs = []
	for root, dirs, files in os.walk(top_path):
		if len(dirs)==0 and len(files)<=1:
			if len(files)==0 or (len(files)>0 and files[0] == ".picasa.ini"):
				del_dirs.append(root)
				
	for dir in del_dirs:
		print "deleting", dir, "..."
		#send2trash(dir)
		
	for dir in dirs:
		if dir.startswith("."):
			dirs.remove(dir)
		

if __name__=="__main__":
	delemptydirs(r"D:\Usuarios\papacrespo\Pictures")