
import os
import sys

def to_flatdir(src_dir, flat_dir):
	for root, dirs, files in os.walk(src_dir):
		for filename in files:
			if not filename.endswith(".ini"):
				try:
					print "Moviendo", filename, "..."
					src = os.path.join(root, filename)
					dst = os.path.join(flat_dir, filename)
					os.rename( src, dst )
				except Exception as ee:
					print filename, "repetida en destino:", ee
					

					
if __name__=="__main__":
	base = r"D:\tmp"
	src_dir = os.path.join(base, "all")
	flat_dir = os.path.join(base, "flat")
	to_flatdir(src_dir, flat_dir)