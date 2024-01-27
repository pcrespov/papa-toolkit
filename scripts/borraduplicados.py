# -*- coding: utf-8 -*- 

import os
from send2trash import send2trash
import hashlib

def evalImageHash(image_path):
	''' Evaluates hash of a given image file'''
	image_hash = None
	with open(image_path) as fh:
		image_file = fh.read()
		image_hash = hashlib.md5(image_file).hexdigest()
	return image_hash

	
def processDuplicates(top_path):
	for root, dirs, files in os.walk(top_path):
		for filename in files:
			name, ext = os.path.splitext(filename)
			for suffix in [' (2)', '-001', ' - copia']:
				if filename.endswith(suffix + ext):
					good = name[:-len(suffix)] + ext
					#print good, name
					original = os.path.join(dirpath, good)
					duplicate = os.path.join(dirpath, filename)
					
					if os.path.exists(original):
						if os.stat(duplicate).st_size==os.stat(original).st_size:
							print "borrando", os.path.basename(duplicate), "..."
							send2trash(duplicate)
					else:
						print "renombrando", os.path.basename(duplicate), "->", os.path.basename(original)
						os.rename(duplicate, original)
		
		for dir in dirs:
			if dir.startswith("."):
				dirs.remove(dir)
	

if __name__=="__main__":
	base = r"D:\tmp\Fotos desconocidas"
	processDuplicates(base)