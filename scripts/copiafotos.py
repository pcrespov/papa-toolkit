import os
import sys
import shutil

base = r'D:\Usuarios\papacrespo\Pictures\Mis escaneos'

dirs = os.listdir(base)
target = []

for name in dirs:
	if 'Ampar' in name:
		#print name
		target.append(name)
		
for name in target:
	src = os.path.join(base, name)
	dest = os.path.join('E:', name)
	print name, '[', len( os.listdir(src) ), ']'
	try:
		shutil.copytree(src, dest)
	except shutil.Error as e:
		print e
	except shutil.OSError as e:
		print e