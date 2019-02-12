import sys, os, shutil, pdb

basePath    = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( basePath + '/Libraries' )

#inPath  = r'C:\Users\danie\Dropbox\Projects\Fellyjish\Vidz'
inPath  = r'F:\20190201'

# inFile  = inPath + '\Day_hr1-4pm-_jelly1_first_20kframes.avi'
inFile  = inPath + '\20190201_631pm.avi'
# outPath = inPath + '\Frames\Day_hr1-4pm-_jelly1_first_20kframes'
outPath = r"C:\Users\Mike's\Your team Dropbox\Michael Abrams\Fellyjish\Vidz" + '\Frames\20190201_631pm'

import image_fns as img
files   = os.listdir(inPath)
for inFile in files:
    print( '\n  >> Extracting: ' + inFile )
    if not os.path.isfile( inPath + '\\' + inFile ): continue
    img.video_to_frames( inPath + '\\' + inFile, inPath + '\\Frames\\' + inFile.split('.')[0] )
    
    print( '  >> Archiving full-length video... ' )
    shutil.copy2( inPath + '\\' + inFile, inPath + '\\Framed\\' + inFile )
    os.remove( inPath + '\\' + inFile )
    
