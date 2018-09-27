import os
import glob

path ='.\printfile'
for infile in glob.glob(os.path.join(path, '*.gcode')):
     os.remove(infile)